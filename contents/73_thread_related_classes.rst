.. _thread_related_classes:

`73. Qt 线程相关类 <http://www.devbean.net/2013/11/qt-study-road-2-thread-related-classes/>`_
==================================================================================================

:作者: 豆子

:日期: 2013年11月26日

希望上一章有关事件循环的内容还没有把你绕晕。本章将重新回到有关线程的相关内容上面来。在前面的章节我们了解了有关QThread类的简单使用。不过，Qt 提供的有关线程的类可不那么简单，否则的话我们也没必要再三强调使用线程一定要万分小心，一不留神就会陷入陷阱。

事实上，Qt 对线程的支持可以追溯到2000年9月22日发布的 Qt 2.2。在这个版本中，Qt 引入了QThread。不过，当时对线程的支持并不是默认开启的。Qt 4.0 开始，线程成为所有平台的默认开启选项（这意味着如果不需要线程，你可以通过编译选项关闭它，不过这不是我们现在的重点）。现在版本的 Qt 引入了很多类来支持线程，下面我们将开始逐一了解它们。

QThread是我们将要详细介绍的第一个类。它也是 Qt 线程类中最核心的底层类。由于 Qt 的跨平台特性，QThread要隐藏掉所有平台相关的代码。

正如前面所说，要使用QThread开始一个线程，我们可以创建它的一个子类，然后覆盖其QThread::run()函数：

.. code-block:: c++

    class Thread : public QThread
    {
    protected:
        void run()
        {
            /* 线程的相关代码 */
        }
    };

然后我们这样使用新建的类来开始一个新的线程：

.. code-block:: c++

    Thread *thread = new Thread;
    thread->start(); // 使用 start() 开始新的线程

注意，从 Qt 4.4 开始，QThread就已经不是抽象类了。QThread::run()不再是纯虚函数，而是有了一个默认的实现。这个默认实现其实是简单地调用了QThread::exec()函数，而这个函数，按照我们前面所说的，其实是开始了一个事件循环（有关这种实现的进一步阐述，我们将在后面的章节详细介绍）。

QRunnable是我们要介绍的第二个类。这是一个轻量级的抽象类，用于开始一个另外线程的任务。这种任务是运行过后就丢弃的。由于这个类是抽象类，我们需要继承QRunnable，然后重写其纯虚函数QRunnable::run()：

.. code-block:: c++

    class Task : public QRunnable
    {
    public:
        void run()
        {
            /* 线程的相关代码 */
        }
    };

要真正执行一个QRunnable对象，我们需要使用QThreadPool类。顾名思义，这个类用于管理一个线程池。通过调用QThreadPool::start(runnable)函数，我们将一个QRunnable对象放入QThreadPool的执行队列。一旦有线程可用，线程池将会选择一个QRunnable对象，然后在那个线程开始执行。所有 Qt 应用程序都有一个全局线程池，我们可以使用QThreadPool::globalInstance()获得这个全局线程池；与此同时，我们也可以自己创建私有的线程池，并进行手动管理。

需要注意的是，QRunnable不是一个QObject，因此也就没有内建的与其它组件交互的机制。为了与其它组件进行交互，你必须自己编写低级线程原语，例如使用 mutex 守护来获取结果等。

QtConcurrent是我们要介绍的最后一个对象。这是一个高级 API，构建于QThreadPool之上，用于处理大多数通用的并行计算模式：map、reduce 以及 filter。它还提供了QtConcurrent::run()函数，用于在另外的线程运行一个函数。注意，QtConcurrent是一个命名空间而不是一个类，因此其中的所有函数都是命名空间内的全局函数。

不同于QThread和QRunnable，QtConcurrent不要求我们使用低级同步原语：所有的QtConcurrent都返回一个QFuture对象。这个对象可以用来查询当前的运算状态（也就是任务的进度），可以用来暂停/回复/取消任务，当然也可以用来获得运算结果。QFutureWatcher类则用来监视QFuture的进度，我们可以用信号槽与QFutureWatcher进行交互（注意，QFuture也没有继承QObject）。

下面我们可以对比一下上面介绍过的三种类：

=========================== ============ ============ ============
特性                        QThread      QRunnable    QtConcurrent
--------------------------- ------------ ------------ ------------
高级API                     x            x            o
面向任务                    x            o            o
内建对暂停/恢复/取消的支持  x            x            o
具有优先级                  o            x            x
可运行事件循环              o            x            x
=========================== ============ ============ ============
