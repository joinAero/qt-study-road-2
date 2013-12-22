.. _thread_and_event_loop:

`72. 线程和事件循环 <http://www.devbean.net/2013/11/qt-study-road-2-thread-and-event-loop/>`_
=============================================================================================

:作者: 豆子

:日期: 2013年11月24日

前面一章我们简单介绍了如何使用QThread实现线程。现在我们开始详细介绍如何“正确”编写多线程程序。我们这里的大部分内容来自于 `Qt的一篇Wiki文档 <http://qt-project.org/wiki/Threads_Events_QObjects>`_ ，有兴趣的童鞋可以去看原文。

在介绍在以前，我们要认识两个术语：

* **可重入的（Reentrant）**：如果一个类允许多个线程使用它的多个实例，并且保证在同一时刻至多只有一个线程访问同一个实例，就称这个类是可重入的。大多数 C++ 类都是可重入的。类似的，一个函数被称为可重入的，如果该函数允许多个线程在同一时刻调用，而每一次的调用都只能使用其独有的数据。全局变量就不是函数独有的数据，而是共享的。换句话说，这意味着类或者函数的使用者必须使用某种额外的机制（比如锁）来控制对对象的实例或共享数据的序列化访问。
* **线程安全（Thread-safe）**：如果多个线程可以在同一时刻使用一个类的对象，就说这个类是线程安全的。如果多个线程可以在同一时刻访问函数的共享数据，就称这个函数是线程安全的。

进一步说，对于一个类，如果不同的实例可以被不同线程同时使用而不受影响，就说这个类是可重入的；如果这个类的所有成员函数都可以被不同线程同时调用而不受影响，即使这些调用针对同一个对象，那么我们就说这个类是线程安全的。由此可以看出，线程安全的语义要强于可重入。接下来，我们从事件开始讨论。之前我们说过，Qt 是事件驱动的。在 Qt 中，事件由一个普通对象表示（QEvent或其子类）。这是事件与信号的一个很大区别：事件总是由某一种类型的对象表示，针对某一个特殊的对象，而信号则没有这种目标对象。所有QObject的子类都可以通过覆盖QObject::event()函数来控制事件的对象。

* QKeyEvent和QMouseEvent对象表示键盘或鼠标的交互，通常由系统的窗口管理器产生；
* QTimerEvent事件在定时器超时时发送给一个QObject，定时器事件通常由操作系统发出；
* QChildEvent在增加或删除子对象时发送给一个QObject，这是由 Qt 应用程序自己发出的。

需要注意的是，与信号不同，事件并不是一产生就被分发。事件产生之后被加入到一个队列中（这里的队列含义同数据结构中的概念，先进先出），该队列即被称为事件队列。事件分发器遍历事件队列，如果发现事件队列中有事件，那么就把这个事件发送给它的目标对象。这个循环被称作事件循环。事件循环的伪代码描述大致如下所示：

.. code-block:: c++

    while (is_active)
    {
        while (!event_queue_is_empty) {
            dispatch_next_event();
        }
        wait_for_more_events();
    }

正如前面所说的，调用QCoreApplication::exec() 函数意味着进入了主循环。我们把事件循环理解为一个无限循环，直到QCoreApplication::exit()或者QCoreApplication::quit()被调用，事件循环才真正退出。

伪代码里面的while会遍历整个事件队列，发送从队列中找到的事件；wait_for_more_events()函数则会阻塞事件循环，直到又有新的事件产生。我们仔细考虑这段代码，在wait_for_more_events()函数所得到的新的事件都应该是由程序外部产生的。因为所有内部事件都应该在事件队列中处理完毕了。因此，我们说事件循环在wait_for_more_events()函数进入休眠，并且可以被下面几种情况唤醒：

* 窗口管理器的动作（键盘、鼠标按键按下、与窗口交互等）；
* 套接字动作（网络传来可读的数据，或者是套接字非阻塞写等）；
* 定时器；
* 由其它线程发出的事件（我们会在后文详细解释这种情况）。

在类 UNIX 系统中，窗口管理器（比如 X11）会通过套接字（Unix Domain 或 TCP/IP）向应用程序发出窗口活动的通知，因为客户端就是通过这种机制与 X 服务器交互的。如果我们决定要实现基于内部的socketpair(2)函数的跨线程事件的派发，那么窗口的管理活动需要唤醒的是：

* 套接字 socket
* 定时器 timer

这也正是select(2)系统调用所做的：它监视窗口活动的一组描述符，如果在一定时间内没有活动，它会发出超时消息（这种超时是可配置的）。Qt 所要做的，就是把select()的返回值转换成一个合适的QEvent子类的对象，然后将其放入事件队列。好了，现在你已经知道事件循环的内部机制了。

至于为什么需要事件循环，我们可以简单列出一个清单：

* **组件的绘制与交互**：QWidget::paintEvent()会在发出QPaintEvent事件时被调用。该事件可以通过内部QWidget::update()调用或者窗口管理器（例如显示一个隐藏的窗口）发出。所有交互事件（键盘、鼠标）也是类似的：这些事件都要求有一个事件循环才能发出。
* **定时器**：长话短说，它们会在select(2)或其他类似的调用超时时被发出，因此你需要允许 Qt 通过返回事件循环来实现这些调用。
* **网络**：所有低级网络类（QTcpSocket、QUdpSocket以及QTcpServer等）都是异步的。当你调用read()函数时，它们仅仅返回已可用的数据；当你调用write()函数时，它们仅仅将写入列入计划列表稍后执行。只有返回事件循环的时候，真正的读写才会执行。注意，这些类也有同步函数（以waitFor开头的函数），但是它们并不推荐使用，就是因为它们会阻塞事件循环。高级的类，例如QNetworkAccessManager则根本不提供同步 API，因此必须要求事件循环。

有了事件循环，你就会想怎样阻塞它。阻塞它的理由可能有很多，例如我就想让QNetworkAccessManager同步执行。在解释为什么 **永远不要阻塞事件循环** 之前，我们要了解究竟什么是“阻塞”。假设我们有一个按钮Button，这个按钮在点击时会发出一个信号。这个信号会与一个Worker对象连接，这个Worker对象会执行很耗时的操作。当点击了按钮之后，我们观察从上到下的函数调用堆栈：

.. code-block:: c++

    main(int, char **)
    QApplication::exec()
    […]
    QWidget::event(QEvent *)
    Button::mousePressEvent(QMouseEvent *)
    Button::clicked()
    […]
    Worker::doWork()

我们在main()函数开始事件循环，也就是常见的QApplication::exec()函数。窗口管理器侦测到鼠标点击后，Qt 会发现并将其转换成QMouseEvent事件，发送给组件的event()函数。这一过程是通过QApplication::notify()函数实现的。注意我们的按钮并没有覆盖event()函数，因此其父类的实现将被执行，也就是QWidget::event()函数。这个函数发现这个事件是一个鼠标点击事件，于是调用了对应的事件处理函数，就是Button::mousePressEvent()函数。我们重写了这个函数，发出Button::clicked()信号，而正是这个信号会调用Worker::doWork()槽函数。有关这一机制我们在前面的事件部分曾有阐述，如果不明白这部分机制，请参考 :ref:`前面的章节 <event_func>` 。

在worker努力工作的时候，事件循环在干什么？或许你已经猜到了答案：什么都没做！事件循环发出了鼠标按下的事件，然后等着事件处理函数返回。此时，它一直是阻塞的，直到Worker::doWork()函数结束。注意，我们使用了“阻塞”一词，也就是说，所谓**阻塞事件循环**，意思是没有事件被派发处理。

在事件就此卡住时， **组件也不会更新自身** （因为QPaintEvent对象还在队列中）， **也不会有其它什么交互发生** （还是同样的原因）， **定时器也不会超时** 并且 **网络交互会越来越慢直到停止** 。也就是说，前面我们大费周折分析的各种依赖事件循环的活动都会停止。这时候，需要窗口管理器会检测到你的应用程序不再处理任何时间，于是 **告诉用户你的程序失去响应** 。这就是为什么我们需要快速地处理事件，并且尽可能快地返回事件循环。

现在，重点来了：我们不可能避免业务逻辑中的耗时操作，那么怎样做才能既可以执行那些耗时的操作，又不会阻塞事件循环呢？一般会有三种解决方案：第一，我们将任务移到另外的线程（正如我们 :ref:`上一章 <thread_intro>` 看到的那样，不过现在我们暂时略过这部分内容）；第二，我们手动强制运行事件循环。想要强制运行事件循环，我们需要在耗时的任务中一遍遍地调用QCoreApplication::processEvents()函数。QCoreApplication::processEvents()函数会发出事件队列中的所有事件，并且立即返回到调用者。仔细想一下，我们在这里所做的，就是模拟了一个事件循环。

另外一种解决方案我们在 :ref:`前面的章节 <access_network_4>` 提到过：使用QEventLoop类重新进入新的事件循环。通过调用QEventLoop::exec()函数，我们重新进入新的事件循环，给QEventLoop::quit()槽函数发送信号则退出这个事件循环。拿前面的例子来说：

.. code-block:: c++

    QEventLoop eventLoop;
    connect(netWorker, &NetWorker::finished,
            &eventLoop, &QEventLoop::quit);
    QNetworkReply *reply = netWorker->get(url);
    replyMap.insert(reply, FetchWeatherInfo);
    eventLoop.exec();

QNetworkReply没有提供阻塞式 API，并且要求有一个事件循环。我们通过一个局部的QEventLoop来达到这一目的：当网络响应完成时，这个局部的事件循环也会退出。

前面我们也强调过：通过“其它的入口”进入事件循环要特别小心：因为它会导致递归调用！现在我们可以看看为什么会导致递归调用了。回过头来看看按钮的例子。当我们在Worker::doWork()槽函数中调用了QCoreApplication::processEvents()函数时，用户再次点击按钮，槽函数Worker::doWork() **又一次** 被调用：

.. code-block:: c++

    main(int, char **)
    QApplication::exec()
    […]
    QWidget::event(QEvent *)
    Button::mousePressEvent(QMouseEvent *)
    Button::clicked()
    […]
    Worker::doWork() // <strong>第一次调用</strong>
    QCoreApplication::processEvents() // <strong>手动发出所有事件</strong>
    […]
    QWidget::event(QEvent * ) // <strong>用户又点击了一下按钮…</strong>
    Button::mousePressEvent(QMouseEvent *)
    Button::clicked() // <strong>又发出了信号…</strong>
    […]
    Worker::doWork() // <strong>递归进入了槽函数！</strong>

当然，这种情况也有解决的办法：我们可以在调用QCoreApplication::processEvents()函数时传入QEventLoop::ExcludeUserInputEvents参数，意思是不要再次派发用户输入事件（这些事件仍旧会保留在事件队列中）。

幸运的是，在 **删除事件** （也就是由QObject::deleteLater()函数加入到事件队列中的事件）中， **没有** 这个问题。这是因为删除事件是由另外的机制处理的。删除事件只有在事件循环有比较小的“嵌套”的情况下才会被处理，而不是调用了deleteLater()函数的那个循环。例如：

.. code-block:: c++

    QObject *object = new QObject;
    object->deleteLater();
    QDialog dialog;
    dialog.exec();

这段代码 **并不会** 造成野指针（注意，QDialog::exec()的调用是嵌套在deleteLater()调用所在的事件循环之内的）。通过QEventLoop进入局部事件循环也是类似的。在 Qt 4.7.3 中，唯一的例外是，在没有事件循环的情况下直接调用deleteLater()函数，那么，之后第一个进入的事件循环会获取这个事件，然后直接将这个对象删除。不过这也是合理的，因为 Qt 本来不知道会执行删除操作的那个“外部的”事件循环，所以第一个事件循环就会直接删除对象。
