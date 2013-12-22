.. _thread_and_qobject:

`74. 线程和 QObject <http://www.devbean.net/2013/12/qt-study-road-2-thread-and-qobject/>`_
==========================================================================================

:作者: 豆子

:日期: 2013年12月03日

前面两个章节我们从事件循环和线程类库两个角度阐述有关线程的问题。本章我们将深入线程间得交互，探讨线程和QObject之间的关系。在某种程度上，这才是多线程编程真正需要注意的问题。

现在我们已经讨论过事件循环。我们说，每一个 Qt 应用程序至少有一个事件循环，就是调用了QCoreApplication::exec()的那个事件循环。不过，QThread也可以开启事件循环。只不过这是一个受限于线程内部的事件循环。因此我们将处于调用main()函数的那个线程，并且由QCoreApplication::exec()创建开启的那个事件循环成为主事件循环，或者直接叫主循环。注意，QCoreApplication::exec()只能在调用main()函数的线程调用。主循环所在的线程就是主线程，也被成为 GUI 线程，因为所有有关 GUI 的操作都必须在这个线程进行。QThread的局部事件循环则可以通过在QThread::run()中调用QThread::exec()开启：

.. code-block:: c++

    class Thread : public QThread
    {
    protected:
        void run() {
            /* ... 初始化 ... */
            exec();
        }
    };

记得我们前面介绍过，Qt 4.4 版本以后，QThread::run()不再是纯虚函数，它会调用QThread::exec()函数。与QCoreApplication一样，QThread也有QThread::quit()和QThread::exit()函数来终止事件循环。

线程的事件循环用于为线程中的所有QObjects对象分发事件；默认情况下，这些对象包括线程中创建的所有对象，或者是在别处创建完成后被移动到该线程的对象（我们会在后面详细介绍“移动”这个问题）。我们说，一个QObject的线程依附性（thread affinity）是指它所在的那个线程。它同样适用于在QThread的构造函数中构建的对象：

.. code-block:: c++

    class MyThread : public QThread
    {
    public:
        MyThread()
        {
            otherObj = new QObject;
        }    
     
    private:
        QObject obj;
        QObject *otherObj;
        QScopedPointer yetAnotherObj;
    };

在我们创建了MyThread对象之后，obj、otherObj和yetAnotherObj的线程依附性是怎样的？是不是就是MyThread所表示的那个线程？要回答这个问题，我们必须看看究竟是哪个线程创建了它们：实际上，是调用了MyThread构造函数的线程创建了它们。因此，这些对象不在MyThread所表示的线程，而是在创建了MyThread的那个线程中。

我们可以通过调用QObject::thread()可以查询一个QObject的线程依附性。注意，在QCoreApplication对象之前创建的QObject没有所谓线程依附性，因此也就没有对象为其派发事件。也就是说，实际是QCoreApplication创建了代表主线程的QThread对象。

.. image:: imgs/74/threadsandobjects.png

我们可以使用线程安全的QCoreApplication::postEvent()函数向一个对象发送事件。它将把事件加入到对象所在的线程的事件队列中，因此，如果这个线程没有运行事件循环，这个事件也不会被派发。

值得注意的一点是，QObject及其所有子类都不是线程安全的（但都是可重入的）。因此，你不能有两个线程同时访问一个QObject对象，除非这个对象的内部数据都已经很好地序列化（例如为每个数据访问加锁）。记住，在你从另外的线程访问一个对象时，它可能正在处理所在线程的事件循环派发的事件！基于同样的原因，你也不能在另外的线程直接delete一个QObject对象，相反，你需要调用QObject::deleteLater()函数，这个函数会给对象所在线程发送一个删除的事件。

此外，QWidget及其子类，以及所有其它 GUI 相关类（即便不是QObject的子类，例如QPixmap），甚至不是可重入的：它们只能在 GUI 线程访问。

QObject的线程依附性是可以改变的，方法是调用QObject::moveToThread()函数。该函数会改变一个对象及其所有子对象的线程依附性。由于QObject不是线程安全的，所以我们只能在该对象所在线程上调用这个函数。也就是说，我们只能在对象所在线程将这个对象移动到另外的线程，不能在另外的线程改变对象的线程依附性。还有一点是，Qt 要求QObject的所有子对象都必须和其父对象在同一线程。这意味着：

不能对有父对象（parent 属性）的对象使用QObject::moveToThread()函数
不能在QThread中以这个QThread本身作为父对象创建对象，例如：

.. code-block:: c++

    class Thread : public QThread {
        void run() {
            QObject *obj = new QObject(this); // 错误！
        }
    };

这是因为QThread对象所依附的线程是创建它的那个线程，而不是它所代表的线程。

Qt 还要求，在代表一个线程的QThread对象销毁之前，所有在这个线程中的对象都必须先delete。要达到这一点并不困难：我们只需在QThread::run()的栈上创建对象即可。

现在的问题是，既然线程创建的对象都只能在函数栈上，怎么能让这些对象与其它线程的对象通信呢？Qt 提供了一个优雅清晰的解决方案：我们在线程的事件队列中加入一个事件，然后在事件处理函数中调用我们所关心的函数。显然这需要线程有一个事件循环。这种机制依赖于 moc 提供的反射：因此，只有信号、槽和使用Q_INVOKABLE宏标记的函数可以在另外的线程中调用。

QMetaObject::invokeMethod()静态函数会这样调用：

.. code-block:: c++

    QMetaObject::invokeMethod(object, "methodName",
                              Qt::QueuedConnection,
                              Q_ARG(type1, arg1),
                              Q_ARG(type2, arg2));

主意，上面函数调用中出现的参数类型都必须提供一个公有构造函数，一个公有的析构函数和一个公有的复制构造函数，并且要使用qRegisterMetaType()函数向 Qt 类型系统注册。

跨线程的信号槽也是类似的。当我们将信号与槽连接起来时，QObject::connect()的最后一个参数将指定连接类型：

* Qt::DirectConnection：直接连接意味着槽函数将在信号发出的线程直接调用
* Qt::QueuedConnection：队列连接意味着向接受者所在线程发送一个事件，该线程的事件循环将获得这个事件，然后之后的某个时刻调用槽函数
* Qt::BlockingQueuedConnection：阻塞的队列连接就像队列连接，但是发送者线程将会阻塞，直到接受者所在线程的事件循环获得这个事件，槽函数被调用之后，函数才会返回
* Qt::AutoConnection：自动连接（默认）意味着如果接受者所在线程就是当前线程，则使用直接连接；否则将使用队列连接

注意在上面每种情况中，发送者所在线程都是无关紧要的！在自动连接情况下，Qt 需要查看 **信号发出的线程** 是不是与 **接受者所在线程** 一致，来决定连接类型。注意，Qt 检查的是 **信号发出的线程** ，而不是信号发出的对象所在的线程！我们可以看看下面的代码：

.. code-block:: c++

    class Thread : public QThread
    {
    Q_OBJECT
    signals:
        void aSignal();
    protected:
        void run() {
            emit aSignal();
        }
    };
     
    /* ... */
    Thread thread;
    Object obj;
    QObject::connect(&thread, SIGNAL(aSignal()), &obj, SLOT(aSlot()));
    thread.start();

aSignal()信号在一个新的线程被发出（也就是Thread所代表的线程）。注意，因为这个线程并不是Object所在的线程（Object所在的线程和Thread所在的是同一个线程，回忆下，信号槽的连接方式与发送者所在线程无关），所以这里将会使用队列连接。

另外一个常见的错误是：

.. code-block:: c++

    class Thread : public QThread
    {
    Q_OBJECT
    slots:
        void aSlot() {
            /* ... */
        }
    protected:
        void run() {
            /* ... */
        }
    };
     
    /* ... */
    Thread thread;
    Object obj;
    QObject::connect(&obj, SIGNAL(aSignal()), &thread, SLOT(aSlot()));
    thread.start();
    obj.emitSignal();

这里的obj发出aSignal()信号时，使用哪种连接方式？答案是：直接连接。因为Thread对象所在线程发出了信号，也就是信号发出的线程与接受者是同一个。在aSlot()槽函数中，我们可以直接访问Thread的某些成员变量，但是注意，在我们访问这些成员变量时，Thread::run()函数可能也在访问！这意味着二者并发进行：这是一个完美的导致崩溃的隐藏bug。

另外一个例子可能更为重要：

.. code-block:: c++

    class Thread : public QThread
    {
    Q_OBJECT
    slots:
        void aSlot() {
            /* ... */
        }
    protected:
        void run() {
            QObject *obj = new Object;
            connect(obj, SIGNAL(aSignal()), this, SLOT(aSlot()));
            /* ... */
        }
    };

为了解决这个问题，我们可以这么做：Thread构造函数中增加一个函数调用：moveToThread(this)：

.. code-block:: c++

    class Thread : public QThread {
    Q_OBJECT
    public:
        Thread() {
            moveToThread(this); // 错误！
        }
     
        /* ... */
    };

实际上，这的确可行（因为Thread的线程依附性被改变了：它所在的线程成了自己），但是这并不是一个好主意。这种代码意味着我们其实误解了线程对象（QThread子类）的设计意图：QThread对象不是线程本身，它们其实是用于管理它所代表的线程的对象。因此，它们应该在另外的线程被使用（通常就是它自己所在的线程），而不是在自己所代表的线程中。

上面问题的最好的解决方案是，将处理任务的部分与管理线程的部分分离。简单来说，我们可以利用一个QObject的子类，使用QObject::moveToThread()改变其线程依附性：

.. code-block:: c++

    class Worker : public QObject
    {
    Q_OBJECT
    public slots:
        void doWork() {
            /* ... */
        }
    };
     
    /* ... */
    QThread *thread = new QThread;
    Worker *worker = new Worker;
    connect(obj, SIGNAL(workReady()), worker, SLOT(doWork()));
    worker->moveToThread(thread);
    thread->start();
