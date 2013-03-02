.. _event_func:

`20. event() <http://www.devbean.net/2012/10/qt-study-road-2-event-func/>`_
===========================================================================

:作者: 豆子

:日期: 2012年10月10日

前面的章节中我们曾经提到 event() 函数。事件对象创建完毕后，Qt 将这个事件对象传递给 QObject 的 event() 函数。event() 函数并不直接处理事件，而是将这些事件对象按照它们不同的类型，分发给不同的事件处理器（event handler）。


如上所述，event() 函数主要用于事件的分发。所以，如果你希望在事件分发之前做一些操作，就可以重写这个 event() 函数了。例如，我们希望在一个 QWidget 组件中监听 tab 键的按下，那么就可以继承 QWidget，并重写它的 event() 函数，来达到这个目的：

.. code-block:: c++

	bool CustomWidget::event(QEvent *e)
	{
	    if (e->type() == QEvent::KeyPress) {
	        QKeyEvent *keyEvent = static_cast<QKeyEvent *>(e);
	        if (keyEvent->key() == Qt::Key_Tab) {
	            qDebug() << "You press tab.";
	            return true;
	        }
	    }
	    return QWidget::event(e);
	}

CustomWidget 是一个普通的 QWidget 子类。我们重写了它的 event() 函数，这个函数有一个 QEvent 对象作为参数，也就是需要转发的事件对象。函数返回值是 bool 类型。如果传入的事件已被识别并且处理，则需要返回 true，否则返回 false。如果返回值是 true，并且，该事件对象设置了 accept()，那么 Qt 会认为这个事件已经处理完毕，不会再将这个事件发送给其它对象，而是会继续处理事件队列中的下一事件。

我们可以通过使用 QEvent::type() 函数可以检查事件的实际类型，其返回值是 QEvent::Type 类型的枚举。我们处理过自己感兴趣的事件之后，可以直接返回 true，表示我们已经对此事件进行了处理；对于其它我们不关心的事件，则需要调用父类的 event() 函数继续转发，否则这个组件就只能处理我们定义的事件了。为了测试这一种情况，我们可以尝试下面的代码：

.. code-block:: c++

	bool CustomTextEdit::event(QEvent *e)
	{
	    if (e->type() == QEvent::KeyPress) {
	        QKeyEvent *keyEvent = static_cast<QKeyEvent *>(e);
	        if (keyEvent->key() == Qt::Key_Tab) {
	            qDebug() << "You press tab.";
	            return true;
	        }
	    }
	    return false;
	}

CustomTextEdit 是 QTextEdit 的一个子类。我们重写了其 event() 函数，却没有调用父类的同名函数。这样，我们的组件就只能处理 Tab 键，再也无法输入任何文本，也不能响应其它事件，比如鼠标点击之后也不会有光标出现。这是因为我们只处理的 KeyPress 类型的事件，并且如果不是 KeyPress 事件，则直接返回 false，鼠标事件根本不会被转发，也就没有了鼠标事件。

通过查看 QObject::event() 的实现，我们可以理解，event() 函数同前面的章节中我们所说的事件处理器有什么联系：

.. code-block:: c++

	//!!! Qt5
	bool QObject::event(QEvent *e)
	{
	    switch (e->type()) {
	    case QEvent::Timer:
	        timerEvent((QTimerEvent*)e);
	        break;
	 
	    case QEvent::ChildAdded:
	    case QEvent::ChildPolished:
	    case QEvent::ChildRemoved:
	        childEvent((QChildEvent*)e);
	        break;
	    // ...
	    default:
	        if (e->type() >= QEvent::User) {
	            customEvent(e);
	            break;
	        }
	        return false;
	    }
	    return true;
	}

这是 Qt 5 中 QObject::event() 函数的源代码（Qt 4 的版本也是类似的）。我们可以看到，同前面我们所说的一样，Qt 也是使用 QEvent::type() 判断事件类型，然后调用了特定的事件处理器。比如，如果 event->type() 返回值是 QEvent::Timer，则调用 timerEvent() 函数。可以想象，QWidget::event() 中一定会有如下的代码：

.. code-block:: c++

	switch (event->type()) {
	    case QEvent::MouseMove:
	        mouseMoveEvent((QMouseEvent*)event);
	        break;
	    // ...
	}

事实也的确如此。timerEvent() 和 mouseMoveEvent() 这样的函数，就是我们前面章节所说的事件处理器 event handler。也就是说，event() 函数中实际是通过事件处理器来响应一个具体的事件。这相当于 event() 函数将具体事件的处理“委托”给具体的事件处理器。而这些事件处理器是 protected virtual 的，因此，我们重写了某一个事件处理器，即可让 Qt 调用我们自己实现的版本。

由此可以见，event() 是一个集中处理不同类型的事件的地方。如果你不想重写一大堆事件处理器，就可以重写这个 event() 函数，通过 QEvent::type() 判断不同的事件。鉴于重写 event() 函数需要十分小心注意父类的同名函数的调用，一不留神就可能出现问题，所以一般还是建议只重写事件处理器（当然，也必须记得是不是应该调用父类的同名处理器）。这其实暗示了 event() 函数的另外一个作用：屏蔽掉某些不需要的事件处理器。正如我们前面的 CustomTextEdit 例子看到的那样，我们创建了一个只能响应 tab 键的组件。这种作用是重写事件处理器所不能实现的。
