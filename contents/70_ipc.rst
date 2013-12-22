.. _ipc:

`70. 进程间通信 <http://www.devbean.net/2013/11/qt-study-road-2-ipc/>`_
=======================================================================

:作者: 豆子

:日期: 2013年11月12日

上一章我们了解了有关进程的基本知识。我们将进程理解为相互独立的正在运行的程序。由于二者是相互独立的，就存在交互的可能性，也就是我们所说的进程间通信（Inter-Process Communication，IPC）。不过也正因此，我们的一些简单的交互方式，比如普通的信号槽机制等，并不适用于进程间的相互通信。我们说过，进程是操作系统的基本调度单元，因此，进程间交互不可避免与操作系统的实现息息相关。

Qt 提供了四种进程间通信的方式：

1. 使用共享内存（shared memory）交互：这是 Qt 提供的一种各个平台均有支持的进程间交互的方式。
2. TCP/IP：其基本思想就是将同一机器上面的两个进程一个当做服务器，一个当做客户端，二者通过网络协议进行交互。除了两个进程是在同一台机器上，这种交互方式与普通的 C/S 程序没有本质区别。Qt 提供了 QNetworkAccessManager 对此进行支持。
3. D-Bus：freedesktop 组织开发的一种低开销、低延迟的 IPC 实现。Qt 提供了 QtDBus 模块，把信号槽机制扩展到进程级别（因此我们前面强调是“普通的”信号槽机制无法实现 IPC），使得开发者可以在一个进程中发出信号，由其它进程的槽函数响应信号。
4. QCOP（Qt COmmunication Protocol）：QCOP 是 Qt 内部的一种通信协议，用于不同的客户端之间在同一地址空间内部或者不同的进程之间的通信。目前，这种机制只用于 Qt for Embedded Linux 版本。

从上面的介绍中可以看到，通用的 IPC 实现大致只有共享内存和 TCP/IP 两种。后者我们前面已经大致介绍过（应用程序级别的 QNetworkAccessManager 或者更底层的 QTcpSocket 等）；本章我们主要介绍前者。

Qt 使用 QSharedMemory 类操作共享内存段。我们可以把 QSharedMemory 看做一种指针，这种指针指向分配出来的一个共享内存段。而这个共享内存段是由底层的操作系统提供，可以供多个线程或进程使用。因此，QSharedMemory 可以看做是专供 Qt 程序访问这个共享内存段的指针。同时，QSharedMemory 还提供了单一线程或进程互斥访问某一内存区域的能力。当我们创建了 QSharedMemory 实例后，可以使用其 create() 函数请求操作系统分配一个共享内存段。如果创建成功（函数返回 true），Qt 会自动将系统分配的共享内存段连接（attach）到本进程。

前面我们说过，IPC 离不开平台特性。作为 IPC 的实现之一的共享内存也遵循这一原则。有关共享内存段，各个平台的实现也有所不同：

* Windows：QSharedMemory 不“拥有”共享内存段。当使用了共享内存段的所有线程或进程中的某一个销毁了 QSharedMemory 实例，或者所有的都退出，Windows 内核会自动释放共享内存段。
* Unix：QSharedMemory “拥有”共享内存段。当最后一个线程或进程同共享内存分离，并且调用了 QSharedMemory 的析构函数之后，Unix 内核会将共享内存段释放。注意，这里与 Windows 不同之处在于，如果使用了共享内存段的线程或进程没有调用 QSharedMemory 的析构函数，程序将会崩溃。
* HP-UX：每个进程只允许连接到一个共享内存段。这意味着在 HP-UX 平台，QSharedMemory 不应被多个线程使用。

下面我们通过一段经典的代码来演示共享内存的使用。这段代码修改自 Qt 自带示例程序（注意这里直接使用了 Qt5，Qt4 与此类似，这里不再赘述）。程序有两个按钮，一个按钮用于加载一张图片，然后将该图片放在共享内存段；第二个按钮用于从共享内存段读取该图片并显示出来。

.. code-block:: c++

    //!!! Qt5

    class QSharedMemory;

    class MainWindow : public QMainWindow
    {
        Q_OBJECT

    public:
        MainWindow(QWidget *parent = 0);
        ~MainWindow();

    private:
        QSharedMemory *sharedMemory;
    };

头文件中，我们将 MainWindow 添加一个 sharedMemory 属性。这就是我们的共享内存段。接下来得实现文件中：

.. code-block:: c++

    const char *KEY_SHARED_MEMORY = "Shared";

    MainWindow::MainWindow(QWidget *parent)
        : QMainWindow(parent),
          sharedMemory(new QSharedMemory(KEY_SHARED_MEMORY, this))
    {
        QWidget *mainWidget = new QWidget(this);
        QVBoxLayout *mainLayout = new QVBoxLayout(mainWidget);
        setCentralWidget(mainWidget);

        QPushButton *saveButton = new QPushButton(tr("Save"), this);
        mainLayout->addWidget(saveButton);
        QLabel *picLabel = new QLabel(this);
        mainLayout->addWidget(picLabel);
        QPushButton *loadButton = new QPushButton(tr("Load"), this);
        mainLayout->addWidget(loadButton);

构造函数初始化列表中我们将 sharedMemory 成员变量进行初始化。注意我们给出一个键（Key），前面说过，我们可以把 QSharedMemory 看做是指向系统共享内存段的指针，而这个键就可以看做指针的名字。多个线程或进程使用同一个共享内存段时，该键值必须相同。接下来是两个按钮和一个标签用于界面显示，这里不再赘述。

下面来看加载图片按钮的实现：

.. code-block:: c++

    connect(saveButton, &QPushButton::clicked, [=]() {
        if (sharedMemory->isAttached()) {
            sharedMemory->detach();
        }
        QString filename = QFileDialog::getOpenFileName(this);
        QPixmap pixmap(filename);
        picLabel->setPixmap(pixmap);

        QBuffer buffer;
        QDataStream out(&buffer);
        buffer.open(QBuffer::ReadWrite);
        out << pixmap;

        int size = buffer.size();
        if (!sharedMemory->create(size)) {
            qDebug() << tr("Create Error: ") << sharedMemory->errorString();
        } else {
            sharedMemory->lock();
            char *to = static_cast(sharedMemory->data());
            const char *from = buffer.data().constData();
            memcpy(to, from, qMin(size, sharedMemory->size()));
            sharedMemory->unlock();
        }
    });

点击加载按钮之后，如果 sharedMemory 已经与某个线程或进程连接，则将其断开（因为我们就要向共享内存段写入内容了）。然后使用 QFileDialog 选择一张图片，利用 QBuffer 将图片数据作为 char * 格式。在即将写入共享内存之前，我们需要请求系统创建一个共享内存段（QSharedMemory::create() 函数），创建成功则开始写入共享内存段。需要注意的是，在读取或写入共享内存时，都需要使用 QSharedMemory::lock() 函数对共享内存段加锁。共享内存段就是一段普通内存，所以我们使用 C 语言标准函数 memcpy() 复制内存段。不要忘记之前我们对共享内存段加锁，在最后需要将其解锁。

接下来是加载按钮的代码：

.. code-block:: c++

    connect(loadButton, &QPushButton::clicked, [=]() {
        if (!sharedMemory->attach()) {
            qDebug() << tr("Attach Error: ") << sharedMemory->errorString();
        } else {
            QBuffer buffer;
            QDataStream in(&buffer);
            QPixmap pixmap;
            sharedMemory->lock();
            buffer.setData(static_cast(sharedMemory->constData()), sharedMemory->size());
            buffer.open(QBuffer::ReadWrite);
            in >> pixmap;
            sharedMemory->unlock();
            sharedMemory->detach();
            picLabel->setPixmap(pixmap);
        }
    });

如果共享内存段已经连接，还是用 QBuffer 读取二进制数据，然后生成图片。注意我们在操作共享内存段时还是要先加锁再解锁。最后在读取完毕后，将共享内存段断开连接。

注意，如果某个共享内存段不是由 Qt 创建的，我们也是可以在 Qt 应用程序中使用。不过这种情况下我们必须使用 QSharedMemory::setNativeKey() 来设置共享内存段。使用原始键（native key）时，QSharedMemory::lock() 函数就会失效，我们必须自己保护共享内存段不会在多线程或进程访问时出现问题。

IPC 使用共享内存通信是一个很常用的开发方法。多个进程间得通信要比多线程间得通信少一些，不过在某一族的应用情形下，比如 QQ 与 QQ 音乐、QQ 影音等共享用户头像，还是非常有用的。
