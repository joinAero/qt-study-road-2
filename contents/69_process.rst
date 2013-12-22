.. _process:

`69. 进程 <http://www.devbean.net/2013/11/qt-study-road-2-process/>`_
=====================================================================

:作者: 豆子

:日期: 2013年11月09日

进程是操作系统的基础之一。一个进程可以认为是一个正在执行的程序。我们可以把进程当做计算机运行时的一个基础单位。关于进程的讨论已经超出了本章的范畴，现在我们假定你是了解这个概念的。

在 Qt 中，我们使用 QProcess 来表示一个进程。这个类可以允许我们的应用程序开启一个新的外部程序，并且与这个程序进行通讯。下面我们用一个非常简单的例子开始我们本章有关进程的阐述。

.. code-block:: c++

    //!!! Qt5
    QString program = "C:/Windows/System32/cmd.exe";
    QStringList arguments;
    arguments << "/c" << "dir" << "C:\\";
    QProcess *cmdProcess = new QProcess; cmdProcess->start(program, arguments);
    QObject::connect(cmdProcess, &QProcess::readyRead, [=] () {
        QTextCodec *codec = QTextCodec::codecForName("GBK");
        QString dir = codec->toUnicode(cmdProcess->readAll());
        qDebug() << dir;
    });

这是一段 Qt5 的程序，并且仅能运行于 Windows 平台。简单来说，这段程序通过 Qt 开启了一个新的进程，这个进程相当于执行了下面的命令：

.. code-block:: none

    C:\Windows\System32\cmd.exe /c dir C:\

注意，我们可以在上面的程序中找到这个命令的每一个字符。事实上，我们可以把一个进程看做执行了一段命令（在 Windows 平台就是控制台命令；在 Linux 平台（包括 Unix）则是执行一个普通的命令，比如 ls）。我们的程序相当于执行了 dir 命令，其参数是 C:\，这是由 arguments 数组决定的（至于为什么我们需要将 dir 命令作为参数传递给 cmd.exe，这是由于 Windows 平台的规定。在 Windows 中，dir 命令并不是一个独立的可执行程序，而是通过 cmd.exe 进行解释；这与 ls 在 Linux 中的地位不同，在 Linux 中，ls 就是一个可执行程序。因此如果你需要在 Linux 中执行 ls，那么 program 的值应该就是 ls ）。

上面程序的运行结果类似于：

.. code-block:: none

    驱动器 C 中的卷是 SYSTEM

    卷的序列号是 EA62-24AB

     C:\ 的目录

    2013/05/05  20:41             1,024 .rnd
    2013/08/22  23:22    <DIR>          PerfLogs
    2013/10/18  07:32    <DIR>          Program Files
    2013/10/30  12:36    <DIR>          Program Files (x86)
    2013/10/31  20:30            12,906 shared.log

    2013/10/18  07:33    <DIR>          Users
    2013/11/06  21:41    <DIR>          Windows
                   2 个文件         13,930 字节
                   5 个目录 22,723,440,640 可用字节

上面的输出会根据不同机器有所不同。豆子是在 Windows 8.1 64位机器上测试的。

为了开启进程，我们将外部程序名字（program）和程序启动参数（arguments）作为参数传给 QProcess::start() 函数。当然，你也可以使用 setProgram() 和 setArguments() 进行设置。此时，QProcess 进入 Starting 状态；当程序开始执行之后，QProcess 进入 Running 状态，并且发出 started() 信号。当进程退出时，QProcess 进入 NotRunning 状态（也是初始状态），并且发出 finished() 信号。finished() 信号以参数的形式提供进程的退出代码和退出状态。如果发送错误，QProcess 会发出 error() 信号

QProcess 允许你将一个进程当做一个顺序访问的 I/O 设备。我们可以使用 write() 函数将数据提供给进程的标准输入；使用 read()、readLine() 或者 getChar() 函数获取其标准输出。由于 QProcess 继承自 QIODevice，因此 QProcess 也可以作为 QXmlReader 的输入或者直接使用 QNetworkAccessManager 将其生成的数据上传到网络。

进程通常有两个预定义的通道：标准输出通道（stdout）和标准错误通道（stderr）。前者就是常规控制台的输出，后者则是由进程输出的错误信息。这两个通道都是独立的数据流，我们可以通过使用 setReadChannel() 函数来切换这两个通道。当进程的当前通道可用时，QProcess 会发出 readReady() 信号。当有了新的标准输出数据时，QProcess 会发出 readyReadStandardOutput() 信号；当有了新的标准错误数据时，则会发出 readyReadStandardError() 信号。我们前面的示例程序就是使用了 readReady() 信号。注意，由于我们是运行在 Windows 平台，Windows 控制台的默认编码是 GBK，为了避免出现乱码，我们必须设置文本的编码方式。

通道的术语可能会引起误会。注意，进程的输出通道对应着 QProcess 的 读 通道，进程的输入通道对应着 QProcess 的 写 通道。这是因为我们使用 QProcess “读取”进程的输出，而我们针对 QProcess 的“写入”则成为进程的输入。QProcess 还可以合并标准输出和标准错误通道，使用 setProcessChannelMode() 函数设置 MergedChannels 即可实现。

另外，QProcess 还允许我们使用 setEnvironment() 为进程设置环境变量，或者使用 setWorkingDirectory() 为进程设置工作目录。

前面我们所说的信号槽机制，类似于前面我们介绍的 QNetworkAccessManager，都是异步的。与 QNetworkAccessManager 不同在于，QProcess 提供了同步函数：

* waitForStarted()：阻塞到进程开始；
* waitForReadyRead()：阻塞到可以从进程的当前读通道读取新的数据；
* waitForBytesWritten()：阻塞到数据写入进程；
* waitForFinished()：阻塞到进程结束；

注意，在主线程（调用了 QApplication::exec() 的线程）调用上面几个函数会让界面失去响应。
