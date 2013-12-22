.. _thread_intro:

.. raw:: html

    <style> .red { color: red; font-weight: bold } </style>

.. role:: red

`71. 线程简介 <http://www.devbean.net/2013/11/qt-study-road-2-thread-intro/>`_
==============================================================================

:作者: 豆子

:日期: 2013年11月18日

前面我们讨论了有关进程以及进程间通讯的相关问题，现在我们开始讨论线程。事实上，现代的程序中，使用线程的概率应该大于进程。特别是在多核时代，CPU 的主频已经进入瓶颈，另辟蹊径地提高程序运行效率就是使用线程，充分利用多核的优势。有关线程和进程的区别已经超出了本章的范畴，我们简单提一句，一个进程可以有一个或更多线程同时运行。线程可以看做是“轻量级进程”，进程完全由操作系统管理，线程即可以由操作系统管理，也可以由应用程序管理。

Qt 使用QThread 来 :red:`管理` 线程。下面来看一个简单的例子：

.. code-block:: c++

    ///!!! Qt5
    MainWindow::MainWindow(QWidget *parent)
        : QMainWindow(parent)
    {
        QWidget *widget = new QWidget(this);
        QVBoxLayout *layout = new QVBoxLayout;
        widget->setLayout(layout);
        QLCDNumber *lcdNumber = new QLCDNumber(this);
        layout->addWidget(lcdNumber);
        QPushButton *button = new QPushButton(tr("Start"), this);
        layout->addWidget(button);
        setCentralWidget(widget);
     
        QTimer *timer = new QTimer(this);
        connect(timer, &QTimer::timeout, [=]() {
            static int sec = 0;
            lcdNumber->display(QString::number(sec++));
        });
     
        WorkerThread *thread = new WorkerThread(this);
        connect(button, &QPushButton::clicked, [=]() {
            timer->start(1);
            for (int i = 0; i < 2000000000; i++);
            timer->stop();
        });
    }

我们的主界面有一个用于显示时间的 LCD 数字面板还有一个用于启动任务的按钮。程序的目的是用户点击按钮，开始一个非常耗时的运算（程序中我们以一个 2000000000 次的循环来替代这个非常耗时的工作，在真实的程序中，这可能是一个网络访问，可能是需要复制一个很大的文件或者其它任务），同时 LCD 开始显示逝去的毫秒数。毫秒数通过一个计时器QTimer进行更新。计算完成后，计时器停止。这是一个很简单的应用，也看不出有任何问题。但是当我们开始运行程序时，问题就来了：点击按钮之后，程序界面直接停止响应，直到循环结束才开始重新更新。

有经验的开发者立即指出，这里需要使用线程。这是因为 Qt 中所有界面都是在 UI 线程中（也被称为主线程，就是执行了QApplication::exec()的线程），在这个线程中执行耗时的操作（比如那个循环），就会阻塞 UI 线程，从而让界面停止响应。界面停止响应，用户体验自然不好，不过更严重的是，有些窗口管理程序会检测到你的程序已经失去响应，可能会建议用户强制停止程序，这样一来你的程序可能就此终止，任务再也无法完成。所以，为了避免这一问题，我们要使用 QThread 开启一个新的线程：

.. code-block:: c++

    ///!!! Qt5
    class WorkerThread : public QThread
    {
        Q_OBJECT
    public:
        WorkerThread(QObject *parent = 0)
            : QThread(parent)
        {
        }
    protected:
        void run()
        {
            for (int i = 0; i < 1000000000; i++);
            emit done();
        }
    signals:
        void done();
    };
     
    MainWindow::MainWindow(QWidget *parent)
        : QMainWindow(parent)
    {
        QWidget *widget = new QWidget(this);
        QVBoxLayout *layout = new QVBoxLayout;
        widget->setLayout(layout);
        lcdNumber = new QLCDNumber(this);
        layout->addWidget(lcdNumber);
        QPushButton *button = new QPushButton(tr("Start"), this);
        layout->addWidget(button);
        setCentralWidget(widget);
     
        QTimer *timer = new QTimer(this);
        connect(timer, &QTimer::timeout, [=]() {
            static int sec = 0;
            lcdNumber->display(QString::number(sec++));
        });
     
        WorkerThread *thread = new WorkerThread(this);
        connect(thread, &WorkerThread::done, timer, &QTimer::stop);
        connect(thread, &WorkerThread::finished, thread, &WorkerThread::deleteLater);
        connect(button, &QPushButton::clicked, [=]() {
            timer->start(1);
            thread->start();
        });
    }

注意，我们增加了一个WorkerThread类。WorkerThread继承自QThread类，重写了其run()函数。我们可以认为，run()函数就是新的线程需要执行的代码。在这里就是要执行这个循环，然后发出计算完成的信号。而在按钮点击的槽函数中，使用QThread::start()函数启动一个线程（注意，这里不是run()函数）。再次运行程序，你会发现现在界面已经不会被阻塞了。另外，我们将WorkerThread::deleteLater()函数与WorkerThread::finished()信号连接起来，当线程完成时，系统可以帮我们清楚线程实例。这里的finished()信号是系统发出的，与我们自定义的done()信号无关。

这是 Qt 线程的最基本的使用方式之一（确切的说，这种使用已经不大推荐使用，不过因为看起来很清晰，而且简单使用起来也没有什么问题，所以还是有必要介绍）。代码看起来很简单，不过，如果你认为 Qt 的多线程编程也很简单，那就大错特错了。Qt 多线程的优势设计使得它使用起来变得容易，但是坑很多，稍不留神就会被绊住，尤其是涉及到与 QObject 交互的情况。稍懂多线程开发的童鞋都会知道，调试多线程开发简直就是煎熬。下面几章，我们会更详细介绍有关多线程编程的相关内容。
