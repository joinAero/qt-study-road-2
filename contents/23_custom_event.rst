.. _custom_event:

`23. 自定义事件 <http://www.devbean.net/2012/10/qt-study-road-2-custom-event/>`_
================================================================================

:作者: 豆子

:日期: 2012年10月23日

尽管 Qt 已经提供了很多事件，但对于更加千变万化的需求来说，有限的事件都是不够的。例如，我要支持一种新的设备，这个设备提供一种崭新的交互方式，那么，这种事件如何处理呢？所以，允许创建自己的事件 类型也就势在必行。即便是不说那种非常极端的例子，在多线程的程序中，自定义事件也是尤其有用。当然，事件也并不是局限在多线程中，它可以用在单线程的程序中，作为一种对象间通讯的机制。那么，为什么我需要使用事件，而不是信号槽呢？主要原因是，事件的分发既可以是同步的，又可以是异步的，而函数的调用或者说是槽的回调总是同步的。事件的另外一个好处是，它可以使用过滤器。


Qt 自定义事件很简单，同其它类库的使用很相似，都是要继承一个类进行扩展。在 Qt 中，你需要继承的类是 QEvent。

继承 QEvent 类，最重要的是提供一个 QEvent::Type 类型的参数，作为自定义事件的类型值。回忆一下，这个 type 是我们在处理事件时用于识别事件类型的代号。比如在 event() 函数中，我们使用 QEvent::type() 获得这个事件类型，然后与我们定义的实际类型对比。

QEvent::Type 是 QEvent 定义的一个枚举。因此，我们可以传递一个 int 值。但是需要注意的是，我们的自定义事件类型不能和已经存在的 type 值重复，否则会有不可预料的错误发生。因为系统会将你新增加的事件当做系统事件进行派发和调用。在 Qt 中，系统保留 0 – 999 的值，也就是说，你的事件 type 要大于 999。这种数值当然非常难记，所以 Qt 定义了两个边界值：QEvent::User 和 QEvent::MaxUser。我们的自定义事件的 type 应该在这两个值的范围之间。其中，QEvent::User 的值是 1000，QEvent::MaxUser 的值是 65535。从这里知道，我们最多可以定义 64536 个事件。通过这两个枚举值，我们可以保证我们自己的事件类型不会覆盖系统定义的事件类型。但是，这样并不能保证自定义事件相互之间不会被覆盖。为了解决这个问题，Qt 提供了一个函数：registerEventType()，用于自定义事件的注册。该函数签名如下：

.. code-block:: c++

	static int QEvent::registerEventType ( int hint = -1 );

这个函数是 static 的，因此可以使用 QEvent 类直接调用。函数接受一个 int 值，其默认值是 -1；函数返回值是向系统注册的新的 Type 类型的值。如果 hint 是合法的，也就是说这个 hint 不会发生任何覆盖（系统的以及其它自定义事件的），则会直接返回这个值；否则，系统会自动分配一个合法值并返回。因此，使用这个函数即可完成 type 值的指定。这个函数是线程安全的，不必另外添加同步。

我们可以在 QEvent 子类中添加自己的事件所需要的数据，然后进行事件的发送。Qt 中提供了两种事件发送方式：

	.. code-block:: c++

		static bool QCoreApplication::sendEvent(QObject *receiver,
		                                        QEvent *event);

	1. 直接将 event 事件发送给 receiver 接受者，使用的是 QCoreApplication::notify() 函数。函数返回值就是事件处理函数的返回值。在事件被发送的时候，event 对象并不会被销毁。通常我们会在栈上创建 event 对象，例如：

	.. code-block:: c++

		QMouseEvent event(QEvent::MouseButtonPress, pos, 0, 0, 0);
		QApplication::sendEvent(mainWindow, &event);

	.. code-block:: c++

		static void QCoreApplication::postEvent(QObject *receiver,
		                                        QEvent *event);

	2. 将 event 事件及其接受者 receiver 一同追加到事件队列中，函数立即返回。

	因为 post 事件队列会持有事件对象，并且在其 post 的时候将其 delete 掉，因此，我们必须在堆上创建 event 对象。当对象被发送之后，再试图访问 event 对象就会出现问题（因为 post 之后，event 对象就会被 delete）。

	当控制权返回到主线程循环是，保存在事件队列中的所有事件都通过 notify() 函数发送出去。

	事件会根据 post 的顺序进行处理。如果你想要改变事件的处理顺序，可以考虑为其指定一个优先级。默认的优先级是 Qt::NormalEventPriority。

	这个函数是线程安全的。

	Qt 还提供了一个函数：

	.. code-block:: c++

		static void QCoreApplication::sendPostedEvents(QObject *receiver,
		                                               int event_type);

	这个函数的作用是，将事件队列中的接受者为 receiver，事件类似为 event_type 的所有事件立即发送给 receiver 进行处理。需要注意的是，来自窗口系统的事件并不由这个函数进行处理，而是 processEvent()。详细信息请参考 Qt API 手册。

现在，我们已经能够自定义事件对象，已经能够将事件发送出去，还剩下最后一步：处理自定义事件。处理自定义事件，同前面我们讲解的那些处理方法没有什么区别。我们可以重写 QObject::customEvent() 函数，该函数接收一个 QEvent 对象作为参数：

.. code-block:: c++

	void QObject::customEvent(QEvent *event);

我们可以通过转换 event 对象类型来判断不同的事件：

.. code-block:: c++

	void CustomWidget::customEvent(QEvent *event) {
	    CustomEvent *customEvent = static_cast<CustomEvent *>(event);
	    // ...
	}

当然，我们也可以在 event() 函数中直接处理：

.. code-block:: c++

	bool CustomWidget::event(QEvent *event) {
	    if (event->type() == MyCustomEventType) {
	        CustomEvent *myEvent = static_cast<CustomEvent *>(event);
	        // processing...
	        return true;
	    }
	    return QWidget::event(event);
	}
