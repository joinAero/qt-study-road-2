.. _snake_3:

`33. 贪吃蛇游戏（3） <http://www.devbean.net/2012/12/qt-study-road-2-snake-3/>`_
================================================================================

:作者: 豆子

:日期: 2012年12月29日

继续前面一章的内容。上次我们讲完了有关蛇的静态部分，也就是绘制部分。现在，我们开始添加游戏控制的代码。首先我们从最简单的四个方向键开始：

.. code-block:: c++

	void Snake::moveLeft()
	{
	    head.rx() -= SNAKE_SIZE;
	    if (head.rx() < -100) {
	        head.rx() = 100;
	    }
	}
	 
	void Snake::moveRight()
	{
	    head.rx() += SNAKE_SIZE;
	    if (head.rx() > 100) {
	        head.rx() = -100;
	    }
	}
	 
	void Snake::moveUp()
	{
	    head.ry() -= SNAKE_SIZE;
	    if (head.ry() < -100) {
	        head.ry() = 100;
	    }
	}
	 
	void Snake::moveDown()
	{
	    head.ry() += SNAKE_SIZE;
	    if (head.ry() > 100) {
	        head.ry() = -100;
	    }
	}

我们有四个以 move 开头的函数，内容都很类似：分别以 SNAKE_SIZE 为基准改变头部坐标，然后与场景边界比较，大于边界值时，设置为边界值。这么做的结果是，当蛇运动到场景最右侧时，会从最左侧出来；当运行到场景最上侧时，会从最下侧出来。

然后我们添加一个比较复杂的函数，借此，我们可以看出 Graphics View Framework 的强大之处：

.. code-block:: c++

	void Snake::handleCollisions()
	{
	    QList collisions = collidingItems();
	 
	    // Check collisions with other objects on screen
	    foreach (QGraphicsItem *collidingItem, collisions) {
	        if (collidingItem->data(GD_Type) == GO_Food) {
	            // Let GameController handle the event by putting another apple
	            controller.snakeAteFood(this, (Food *)collidingItem);
	            growing += 1;
	        }
	    }
	 
	    // Check snake eating itself
	    if (tail.contains(head)) {
	        controller.snakeAteItself(this);
	    }
	}

顾名思义，handleCollisions() 的意思是处理碰撞，也就是所谓的“碰撞检测”。首先，我们使用 collidingItems() 取得所有碰撞的元素。这个函数的签名是：

.. code-block:: c++

	QList<QGraphicsItem *> QGraphicsItem::collidingItems(
	        Qt::ItemSelectionMode mode = Qt::IntersectsItemShape) const

该函数返回与这个元素碰撞的所有元素。Graphcis View Framework 提供了四种碰撞检测的方式：

* Qt::ContainsItemShape：如果被检测物的形状（shape()）完全包含在检测物内，算做碰撞；
* Qt::IntersectsItemShape：如果被检测物的形状（shape()）与检测物有交集，算做碰撞；
* Qt::ContainsItemBoundingRect：如果被检测物的包含矩形（boundingRect()）完全包含在检测物内，算做碰撞；
* Qt::IntersectsItemBoundingRect：如果被检测物的包含矩形（boundingRect()）与检测物有交集，算做碰撞。

注意，该函数默认是 Qt::IntersectsItemShape。回忆一下，我们之前编写的代码，Food 的 boundingRect() 要大于其实际值，却不影响我们的游戏逻辑判断，这就是原因：因为我们使用的是 Qt::IntersectsItemShape 判断检测，这与 boundingRect() 无关。

后面的代码就很简单了。我们遍历所有被碰撞的元素，如果是食物，则进行吃食物的算法，同时将蛇的长度加 1。最后，如果身体包含了头，那就是蛇吃了自己的身体。

还记得我们在 Food 类中有这么一句：

.. code-block:: c++

	setData(GD_Type, GO_Food);

QGraphicsItem::setData() 以键值对的形式设置元素的自定义数据。所谓自定义数据，就是对应用程序有所帮助的用户数据。Qt 不会使用这种机制来存储数据，因此你可以放心地将所需要的数据存储到元素对象。例如，我们在 Food 的构造函数中，将 GD_Type 的值设置为 GO_Food。那么，这里我们取出 GD_Type，如果其值是 GO_Food，意味着这个 QGraphicsItem 就是一个 Food，因此我们可以将其安全地进行后面的类型转换，从而完成下面的代码。

下面是 advance() 函数的代码：

.. code-block:: c++

	void Snake::advance(int step)
	{
	    if (!step) {
	        return;
	    }
	    if (tickCounter++ % speed != 0) {
	        return;
	    }
	    if (moveDirection == NoMove) {
	        return;
	    }
	 
	    if (growing > 0) {
	        QPointF tailPoint = head;
	        tail << tailPoint;
	        growing -= 1;
	    } else {
	        tail.takeFirst();
	        tail << head;
	    }
	 
	    switch (moveDirection) {
	        case MoveLeft:
	            moveLeft();
	            break;
	        case MoveRight:
	            moveRight();
	            break;
	        case MoveUp:
	            moveUp();
	            break;
	        case MoveDown:
	            moveDown();
	            break;
	    }
	 
	    setPos(head);
	    handleCollisions();
	}

QGraphicsItem::advance() 函数接受一个 int 作为参数。这个 int 代表该函数被调用的时间。QGraphicsItem::advance() 函数会被 QGraphicsScene::advance() 函数调用两次：第一次时这个 int 为 0，代表即将开始调用；第二次这个 int 为 1，代表已经开始调用。在我们的代码中，我们只使用不为 0 的阶段，因此当 !step 时，函数直接返回。

tickCounter 实际是我们内部的一个计时器。我们使用 speed 作为蛇的两次动作的间隔时间，直接影响到游戏的难度。speed 值越大，两次运动的间隔时间越大，游戏越简单。这是因为随着 speed 的增大，tickCounter % speed != 0 的次数响应越多，刷新的次数就会越少，蛇运动得越慢。

moveDirection 显然就是运动方向，当是 NoMove 时，函数直接返回。

growing 是正在增长的方格数。当其大于 0 时，我们将头部追加到尾部的位置，同时减少一个方格；当其小于 0 时，我们删除第一个，然后把头部添加进去。我们可以把 growing 看做即将发生的变化。比如，我们将 growing 初始化为 7。第一次运行 advance() 时，由于 7 > 1，因此将头部追加，然后 growing 减少 1。直到 growing 为 0，此时，蛇的长度不再发生变化，直到我们吃了一个食物。

下面是相应的方向时需要调用对应的函数。最后，我们设置元素的坐标，同时检测碰撞。
