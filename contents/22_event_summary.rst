.. _event_summary:

`22. 事件总结 <http://www.devbean.net/2012/10/qt-study-road-2-event-summary/>`_
===============================================================================

:作者: 豆子

:日期: 2012年10月16日

Qt 的事件是整个 Qt 框架的核心机制之一，也比较复杂。说它复杂，更多是因为它涉及到的函数众多，而处理方法也很多，有时候让人难以选择。现在我们简单总结一下 Qt 中的事件机制。


Qt 中有很多种事件：鼠标事件、键盘事件、大小改变的事件、位置移动的事件等等。如何处理这些事件，实际有两种选择：

1. 所有事件对应一个事件处理函数，在这个事件处理函数中用一个很大的分支语句进行选择，其代表作就是 win32 API 的 WndProc() 函数：

.. code-block:: c++

	LRESULT CALLBACK WndProc(HWND hWnd,
	                         UINT message,
	                         WPARAM wParam,
	                         LPARAM lParam)

在这个函数中，我们需要使用 switch 语句，选择 message 参数的类型进行处理，典型代码是：


.. code-block:: c++

	switch(message)
	{
	    case WM_PAINT:
	        // ...
	        break;
	    case WM_DESTROY:
	        // ...
	        break;
	    ...
	}

每一种事件对应一个事件处理函数。Qt 就是使用的这么一种机制：

* mouseEvent()
* keyPressEvent()
* ...

Qt 具有这么多种事件处理函数，肯定有一个地方对其进行分发，否则，Qt 怎么知道哪一种事件调用哪一个事件处理函数呢？这个分发的函数，就是 event()。显然，当 QMouseEvent 产生之后，event() 函数将其分发给 mouseEvent() 事件处理器进行处理。

event() 函数会有两个问题：

1. event() 函数是一个 protected 的函数，这意味着我们要想重写 event()，必须继承一个已有的类。试想，我的程序根本不想要鼠标事件，程序中所有组件都不允许处理鼠标事件，是不是我得继承所有组件，一一重写其 event() 函数？protected 函数带来的另外一个问题是，如果我基于第三方库进行开发，而对方没有提供源代码，只有一个链接库，其它都是封装好的。我怎么去继承这种库中的组件呢？
2. event() 函数的确有一定的控制，不过有时候我的需求更严格一些：我希望那些组件根本看不到这种事件。event() 函数虽然可以拦截，但其实也是接收到了 QMouseEvent 对象。我连让它收都收不到。这样做的好处是，模拟一种系统根本没有那个时间的效果，所以其它组件根本不会收到这个事件，也就无需修改自己的事件处理函数。这种需求怎么办呢？

这两个问题是 event() 函数无法处理的。于是，Qt 提供了另外一种解决方案：事件过滤器。事件过滤器给我们一种能力，让我们能够完全移除某种事件。事件过滤器可以安装到任意 QObject 类型上面，并且可以安装多个。如果要实现全局的事件过滤器，则可以安装到 QApplication 或者 QCoreApplication 上面。这里需要注意的是，如果使用 installEventFilter() 函数给一个对象安装事件过滤器，那么该事件过滤器只对该对象有效，只有这个对象的事件需要先传递给事件过滤器的 eventFilter() 函数进行过滤，其它对象不受影响。如果给 QApplication 对象安装事件过滤器，那么该过滤器对程序中的每一个对象都有效，任何对象的事件都是先传给 eventFilter() 函数。

事件过滤器可以解决刚刚我们提出的 event() 函数的两点不足：首先，事件过滤器不是 protected 的，因此我们可以向任何 QObject 子类安装事件过滤器；其次，事件过滤器在目标对象接收到事件之前进行处理，如果我们将时间过滤掉，目标对象根本不会见到这个事件。

事实上，还有一种方法，我们没有介绍。Qt 事件的调用最终都会追溯到 QCoreApplication::notify() 函数，因此，最大的控制权实际上是重写 QCoreApplication::notify()。这个函数的声明是：

.. code-block:: c++

	virtual bool QCoreApplication::notify ( QObject * receiver, QEvent * event );

该函数会将 event 发送给 receiver，也就是调用 receiver->event(event)，其返回值就是来自 receiver 的事件处理器。注意，这个函数为任意线程的任意对象的任意事件调用，因此，它不存在事件过滤器的线程的问题。不过我们并不推荐这么做，因为 notify() 函数只有一个，而事件过滤器要灵活得多。

现在我们可以总结一下 Qt 的事件处理，实际上是有五个层次：

1. 重写 paintEvent()、mousePressEvent() 等事件处理函数。这是最普通、最简单的形式，同时功能也最简单。
2. 重写 event() 函数。event() 函数是所有对象的事件入口，QObject 和 QWidget 中的实现，默认是把事件传递给特定的事件处理函数。
3. 在特定对象上面安装事件过滤器。该过滤器仅过滤该对象接收到的事件。
4. 在 QCoreApplication::instance() 上面安装事件过滤器。该过滤器将过滤所有对象的所有事件，因此和 notify() 函数一样强大，但是它更灵活，因为可以安装多个过滤器。全局的事件过滤器可以看到 disabled 组件上面发出的鼠标事件。全局过滤器有一个问题：只能用在主线程。
5. 重写 QCoreApplication::notify() 函数。这是最强大的，和全局事件过滤器一样提供完全控制，并且不受线程的限制。但是全局范围内只能有一个被使用（因为 QCoreApplication 是单例的）。

为了进一步了解这几个层次的事件处理方式的调用顺序，我们可以编写一个测试代码：

.. code-block:: c++

	class Label : public QWidget
	{
	public:
	    Label()
	    {
	        installEventFilter(this);
	    }
	 
	    bool eventFilter(QObject *watched, QEvent *event)
	    {
	        if (watched == this) {
	            if (event->type() == QEvent::MouseButtonPress) {
	                qDebug() << "eventFilter";
	            }
	        }
	        return false;
	    }
	 
	protected:
	    void mousePressEvent(QMouseEvent *)
	    {
	        qDebug() << "mousePressEvent";
	    }
	 
	    bool event(QEvent *e)
	    {
	        if (e->type() == QEvent::MouseButtonPress) {
	            qDebug() << "event";
	        }
	        return QWidget::event(e);
	    }
	};
	 
	class EventFilter : public QObject
	{
	public:
	    EventFilter(QObject *watched, QObject *parent = 0) :
	        QObject(parent),
	        m_watched(watched)
	    {
	    }
	 
	    bool eventFilter(QObject *watched, QEvent *event)
	    {
	        if (watched == m_watched) {
	            if (event->type() == QEvent::MouseButtonPress) {
	                qDebug() << "QApplication::eventFilter";
	            }
	        }
	        return false;
	    }
	 
	private:
	    QObject *m_watched;
	};
	 
	int main(int argc, char *argv[])
	{
	    QApplication app(argc, argv);
	    Label label;
	    app.installEventFilter(new EventFilter(&label, &label));
	    label.show();
	    return app.exec();
	}

我们可以看到，鼠标点击之后的输出结果是：

.. code-block:: none

	QApplication::eventFilter 
	eventFilter 
	event 
	mousePressEvent

因此可以知道，全局事件过滤器被第一个调用，之后是该对象上面的事件过滤器，其次是 event() 函数，最后是特定的事件处理函数。
