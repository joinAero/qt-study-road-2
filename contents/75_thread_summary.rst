.. _thread_summary:

`75. 线程总结 <http://www.devbean.net/2013/12/qt-study-road-2-thread-summary/>`_
================================================================================

:作者: 豆子

:日期: 2013年12月09日

前面我们已经详细介绍过有关线程的一些值得注意的事项。现在我们开始对线程做一些总结。

有关线程，你可以做的是：

* 在QThread子类添加信号。这是绝对安全的，并且也是正确的（前面我们已经详细介绍过，发送者的线程依附性没有关系）

不应该做的是：

* 调用moveToThread(this)函数
* 指定连接类型：这通常意味着你正在做错误的事情，比如将QThread控制接口与业务逻辑混杂在了一起（而这应该放在该线程的一个独立对象中）
* 在QThread子类添加槽函数：这意味着它们将在错误的线程被调用，也就是QThread对象所在线程，而不是QThread对象管理的线程。这又需要你指定连接类型或者调用moveToThread(this)函数
* 使用QThread::terminate()函数

不能做的是：

* 在线程还在运行时退出程序。使用QThread::wait()函数等待线程结束
* 在QThread对象所管理的线程仍在运行时就销毁该对象。如果你需要某种“自行销毁”的操作，你可以把finished()信号同deleteLater()槽连接起来

那么，下面一个问题是：我什么时候应该使用线程？

**首先，当你不得不使用同步 API 的时候。**

如果你需要使用一个没有非阻塞 API 的库或代码（所谓非阻塞 API，很大程度上就是指信号槽、事件、回调等），那么，避免事件循环被阻塞的解决方案就是使用进程或者线程。不过，由于开启一个新的工作进程，让这个进程去完成任务，然后再与当前进程进行通信，这一系列操作的代价都要比开启线程要昂贵得多，所以，线程通常是最好的选择。

一个很好的例子是地址解析服务。注意我们这里并不讨论任何第三方 API，仅仅假设一个有这样功能的库。这个库的工作是将一个主机名转换成地址。这个过程需要去到一个系统（也就是域名系统，Domain Name System, DNS）执行查询，这个系统通常是一个远程系统。一般这种响应应该瞬间完成，但是并不排除远程服务器失败、某些包可能会丢失、网络可能失去链接等等。简单来说，我们的查询可能会等几十秒钟。

UNIX 系统上的标准 API 是阻塞的（不仅是旧的gethostbyname(3)，就连新的getservbyname(3)和getaddrinfo(3)也是一样）。Qt 提供的QHostInfo类同样用于地址解析，默认情况下，内部使用一个QThreadPool提供后台运行方式的查询（如果关闭了 Qt 的线程支持，则提供阻塞式 API）。

另外一个例子是图像加载和缩放。QImageReader和QImage只提供了阻塞式 API，允许我们从设备读取图片，或者是缩放到不同的分辨率。如果你需要处理很大的图像，这种任务会花费几十秒钟。

**其次，当你希望扩展到多核应用的时候。**

线程允许你的程序利用多核系统的优势。每一个线程都可以被操作系统独立调度，如果你的程序运行在多核机器上，调度器很可能会将每一个线程分配到各自的处理器上面运行。

举个例子，一个程序需要为很多图像生成缩略图。一个具有固定 n 个线程的线程池，每一个线程交给系统中的一个可用的 CPU 进行处理（我们可以使用QThread::idealThreadCount()获取可用的 CPU 数）。这样的调度将会把图像缩放工作交给所有线程执行，从而有效地提升效率，几乎达到与 CPU 数的线性提升（实际情况不会这么简单，因为有时候 CPU 并不是瓶颈所在）。

**第三，当你不想被别人阻塞的时候。**

这是一个相当高级的话题，所以你现在可以暂时不看这段。这个问题的一个很好的例子是在 WebKit 中使用QNetworkAccessManager。WebKit 是一个现代的浏览器引擎。它帮助我们展示网页。Qt 中的QWebView就是使用的 WebKit。

QNetworkAccessManager则是 Qt 处理 HTTP 请求和响应的通用类。我们可以将它看做浏览器的网络引擎。在 Qt 4.8 之前，这个类没有使用任何协助工作线程，所有的网络处理都是在QNetworkAccessManager及其QNetworkReply所在线程完成。

虽然在网络处理中不使用线程是一个好主意，但它也有一个很大的缺点：如果你不能及时从 socket 读取数据，内核缓冲区将会被填满，于是开始丢包，传输速度将会直线下降。

socket 活动（也就是从一个 socket 读取一些可用的数据）是由 Qt 的事件循环管理的。因此，阻塞事件循环将会导致传输性能的损失，因为没有人会获得有数据可读的通知，因此也就没有人能够读取这些数据。

但是什么会阻塞事件循环？最坏的答案是：WebKit 自己！只要收到数据，WebKit 就开始生成网页布局。不幸的是，这个布局的过程非常复杂和耗时，因此它会阻塞事件循环。尽管阻塞时间很短，但是足以影响到正常的数据传输（宽带连接在这里发挥了作用，在很短时间内就可以塞满内核缓冲区）。

总结一下上面所说的内容：

* WebKit 发起一次请求
* 从服务器响应获取一些数据
* WebKit 利用到达的数据开始进行网页布局，阻塞事件循环
* 由于事件循环被阻塞，也就没有了可用的事件循环，于是操作系统接收了到达的数据，但是却不能从QNetworkAccessManager的 socket 读取
* 内核缓冲区被填满，传输速度变慢

网页的整体加载时间被自身的传输速度的降低而变得越来越坏。

注意，由于QNetworkAccessManager和QNetworkReply都是QObject，所以它们都不是线程安全的，因此你不能将它们移动到另外的线程继续使用。因为它们可能同时有两个线程访问：你自己的和它们所在的线程，这是因为派发给它们的事件会由后面一个线程的事件循环发出，但你不能确定哪一线程是“后面一个”。

Qt 4.8 之后，QNetworkAccessManager默认会在一个独立的线程处理 HTTP 请求，所以导致 GUI 失去响应以及操作系统缓冲区过快填满的问题应该已经被解决了。

那么，什么情况下不应该使用线程呢？

**定时器**

这可能是最容易误用线程的情况了。如果我们需要每隔一段时间调用一个函数，很多人可能会这么写代码：

.. code-block:: c++

    // 最错误的代码
    while (condition) {
        doWork();
        sleep(1); // C 库里面的 sleep(3) 函数
    }

当读过我们前面的文章之后，可能又会引入线程，改成这样的代码：

.. code-block:: c++

    // 错误的代码
    class Thread : public QThread {
    protected:
        void run() {
            while (condition) {
                // 注意，如果我们要在别的线程修改 condition，那么它也需要加锁
                doWork();
                sleep(1); // 这次是 QThread::sleep()
            }
        }
    };

最好最简单的实现是使用定时器，比如QTimer，设置 1s 超时，然后将doWork()作为槽：

.. code-block:: c++

    class Worker : public QObject
    {
    Q_OBJECT
    public:
        Worker()
        {
            connect(&timer, SIGNAL(timeout()), this, SLOT(doWork()));
            timer.start(1000);
        }
    private slots:
        void doWork()
        {
            /* ... */
        }
    private:
        QTimer timer;
    };

我们所需要的就是开始事件循环，然后每隔一秒doWork()就会被自动调用。

**网络/状态机**

下面是一个很常见的处理网络操作的设计模式：

.. code-block:: c++

    socket->connect(host);
    socket->waitForConnected();
     
    data = getData();
    socket->write(data);
    socket->waitForBytesWritten();
     
    socket->waitForReadyRead();
    socket->read(response);
     
    reply = process(response);
     
    socket->write(reply);
    socket->waitForBytesWritten();
    /* ... */

在经过前面几章的介绍之后，不用多说，我们就会发现这里的问题：大量的waitFor*()函数会阻塞事件循环，冻结 UI 界面等等。注意，上面的代码还没有加入异常处理，否则的话肯定会更复杂。这段代码的错误在于，我们的网络实际是异步的，如果我们非得按照同步方式处理，就像拿起枪打自己的脚。为了解决这个问题，很多人会简单地将这段代码移动到一个新的线程。

一个更抽象的例子是：

.. code-block:: c++

    result = process_one_thing();
     
    if (result->something()) {
        process_this();
    } else {
        process_that();
    }
     
    wait_for_user_input();
    input = read_user_input();
    process_user_input(input);
    /* ... */

这段抽象的代码与前面网络的例子有“异曲同工之妙”。

让我们回过头来看看这段代码究竟是做了什么：我们实际是想创建一个状态机，这个状态机要根据用户的输入作出合理的响应。例如我们网络的例子，我们实际是想要构建这样的东西：

.. code-block:: none

    空闲 → 正在连接（调用<code>connectToHost()</code>）
    正在连接 → 成功连接（发出<code>connected()</code>信号）
    成功连接 → 发送登录数据（将登录数据发送到服务器）
    发送登录数据 → 登录成功（服务器返回 ACK）
    发送登录数据 → 登录失败（服务器返回 NACK）

以此类推。

既然知道我们的实际目的，我们就可以修改代码来创建一个真正的状态机（Qt 甚至提供了一个状态机类：QStateMachine）。创建状态机最简单的方法是使用一个枚举来记住当前状态。我们可以编写如下代码：

.. code-block:: c++

    class Object : public QObject
    {
        Q_OBJECT
        enum State {
            State1, State2, State3 /* ... */
        };
        State state;
    public:
        Object() : state(State1)
        {
            connect(source, SIGNAL(ready()), this, SLOT(doWork()));
        }
    private slots:
        void doWork() {
            switch (state) {
            case State1:
                /* ... */
                state = State2;
                break;
            case State2:
                /* ... */
                state = State3;
                break;
            /* ... */
            }
        }
    };

source对象是哪来的？这个对象其实就是我们关心的对象：例如，在网络的例子中，我们可能希望把 socket 的QAbstractSocket::connected()或者QIODevice::readyRead()信号与我们的槽函数连接起来。当然，我们很容易添加更多更合适的代码（比如错误处理，使用QAbstractSocket::error()信号就可以了）。这种代码是真正异步、信号驱动的设计。

**将任务分割成若干部分**

假设我们有一个很耗时的计算，我们不能简单地将它移动到另外的线程（或者是我们根本无法移动它，比如这个任务必须在 GUI 线程完成）。如果我们将这个计算任务分割成小块，那么我们就可以及时返回事件循环，从而让事件循环继续派发事件，调用处理下一个小块的函数。回一下如何实现队列连接，我们就可以轻松完成这个任务：将事件提交到接收对象所在线程的事件循环；当事件发出时，响应函数就会被调用。

我们可以使用QMetaObject::invokeMethod()函数，通过指定Qt::QueuedConnection作为调用类型来达到相同的效果。不过这要求函数必须是内省的，也就是说这个函数要么是一个槽函数，要么标记有Q_INVOKABLE宏。如果我们还需要传递参数，我们需要使用qRegisterMetaType()函数将参数注册到 Qt 元类型系统。下面是代码示例：

.. code-block:: c++

    class Worker : public QObject
    {
        Q_OBJECT
    public slots:
        void startProcessing()
        {
            processItem(0);
        }
        void processItem(int index)
        {
            /* 处理 items[index] ... */

            if (index < numberOfItems) {
                QMetaObject::invokeMethod(this,
                                          "processItem",
                                          Qt::QueuedConnection,
                                          Q_ARG(int, index + 1));
            }
        }
    };

由于没有任何线程调用，所以我们可以轻易对这种计算任务执行暂停/恢复/取消，以及获取结果。

至此，我们利用五个章节将有关线程的问题简单介绍了下。线程应该说是全部设计里面最复杂的部分之一，所以这部分内容也会比较困难。在实际运用中肯定会更多的问题，这就只能让我们具体分析了。
