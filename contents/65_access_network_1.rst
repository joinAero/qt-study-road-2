.. _access_network_1:

`65. 访问网络（1） <http://www.devbean.net/2013/10/qt-study-road-2-access-network-1/>`_
=======================================================================================

:作者: 豆子

:日期: 2013年10月11日

现在的应用程序很少有纯粹单机的。大部分为了各种目的都需要联网操作。为此，Qt 提供了自己的网络访问库，方便我们对网络资源进行访问。本章我们将介绍如何使用 Qt 进行最基本的网络访问。

Qt 进行网络访问的类是QNetworkAccessManager，这是一个名字相当长的类，不过使用起来并不像它的名字一样复杂。为了使用网络相关的类，你需要在 pro 文件中添加QT += network。

QNetworkAccessManager类允许应用程序发送网络请求以及接受服务器的响应。事实上，Qt 的整个访问网络 API 都是围绕着这个类进行的。QNetworkAccessManager保存发送的请求的最基本的配置信息，包含了代理和缓存的设置。最好的是，这个 API 本身就是异步设计，这意味着我们不需要自己为其开启线程，以防止界面被锁死（这里我们可以简单了解下，Qt 的界面活动是在一个主线程中进行。网络访问是一个相当耗时的操作，如果整个网络访问的过程以同步的形式在主线程进行，则当网络访问没有返回时，主线程会被阻塞，界面就会被锁死，不能执行任何响应，甚至包括一个代表响应进度的滚动条都会被卡死在那里。这种设计显然是不友好的。）。异步的设计避免了这一系列的问题，但是却要求我们使用更多的代码来监听返回。这类似于我们前面提到的QDialog::exec()和QDialog::show()之间的区别。QNetworkAccessManager是使用信号槽来达到这一目的的。

一个应用程序仅需要一个QNetworkAccessManager类的实例。所以，虽然QNetworkAccessManager本身没有被设计为单例，但是我们应该把它当做单例使用。一旦一个QNetworkAccessManager实例创建完毕，我们就可以使用它发送网络请求。这些请求都返回QNetworkReply对象作为响应。这个对象一般会包含有服务器响应的数据。

下面我们用一个例子来看如何使用QNetworkAccessManager进行网络访问。这个例子不仅会介绍QNetworkAccessManager的使用，还将设计到一些关于程序设计的细节。

我们的程序是一个简单的天气预报的程序，使用 OpenWeatherMap 的 API 获取数据。我们可以在 `这里 <http://api.openweathermap.org/api>`_ 找到其 API 的具体介绍。

我们前面说过，一般一个应用使用一个QNetworkAccessManager就可以满足需要，因此我们自己封装一个NetWorker类，并把这个类作为单例。注意，我们的代码使用了 Qt5 进行编译，因此如果你需要将代码使用 Qt4 编译，请自行修改相关部分。

.. code-block:: c++

    // !!! Qt5
    #ifndef NETWORKER_H
    #define NETWORKER_H
     
    #include <QObject>
     
    class QNetworkReply;
     
    class NetWorker : public QObject
    {
        Q_OBJECT
    public:
        static NetWorker * instance();
        ~NetWorker();
     
        void get(const QString &url);
    signals:
        void finished(QNetworkReply *reply);
    private:
        class Private;
        friend class Private;
        Private *d;
     
        explicit NetWorker(QObject *parent = 0);
        NetWorker(const NetWorker &) Q_DECL_EQ_DELETE;
        NetWorker& operator=(NetWorker rhs) Q_DECL_EQ_DELETE;
    };
     
    #endif // NETWORKER_H

NetWorker是一个单例类，因此它有一个instance()函数用来获得这唯一的实例。作为单例模式，要求构造函数、拷贝构造函数和赋值运算符都是私有的，因此我们将这三个函数都放在 private 块中。注意我们增加了一个Q_DECL_EQ_DELETE宏。这个宏是 Qt5 新增加的，意思是将它所修饰的函数声明为 deleted（这是 C++11 的新特性）。如果编译器支持= delete语法，则这个宏将会展开为= delete，否则则展开为空。我们的NetWorker只有一个get函数，顾名思义，这个函数会执行 HTTP GET 操作；一个信号finished()，会在获取到服务器响应后发出。private 块中还有三行关于Private的代码：

.. code-block:: c++

    class Private;
    friend class Private;
    Private *d;

这里声明了一个NetWorker的内部类，然后声明了这个内部类的 d 指针。d 指针是 C++ 程序常用的一种设计模式。它的存在于 C++ 程序的编译有关。在 C++ 中，保持二进制兼容性非常重要。如果你能够保持二进制兼容，则当以后升级库代码时，用户不需要重新编译自己的程序即可直接运行（如果你使用 Qt5.0 编译了一个程序，这个程序不需要重新编译就可以运行在 Qt5.1 下，这就是二进制兼容；如果不需要修改源代码，但是必须重新编译才能运行，则是源代码兼容；如果必须修改源代码并且再经过编译，例如从 Qt4 升级到 Qt5，则称二者是不兼容的）。保持二进制兼容的很重要的一个原则是不要随意增加、删除成员变量。因为这会导致类成员的寻址偏移量错误，从而破坏二进制兼容。为了避免这个问题，我们将一个类的所有私有变量全部放进一个单独的辅助类中，而在需要使用这些数据的类值提供一个这个辅助类的指针。注意，由于我们的辅助类是私有的，用户不能使用它，所以针对这个辅助类的修改不会影响到外部类，从而保证了二进制兼容。关于二进制兼容的问题，我们会在以后的文章中更详细的说明，这里仅作此简单介绍。

下面来看NetWorker的实现。

.. code-block:: c++

    class NetWorker::Private
    {
    public:
        Private(NetWorker *q) :
            manager(new QNetworkAccessManager(q))
        {}
     
        QNetworkAccessManager *manager;
    };

Private是NetWorker的内部类，扮演者前面我们所说的那个辅助类的角色。NetWorker::Private类主要有一个成员变量QNetworkAccessManager \*，把QNetworkAccessManager封装起来。NetWorker::Private需要其被辅助的类NetWorker的指针，目的是作为QNetworkAccessManager的 parent，以便NetWorker析构时能够自动将QNetworkAccessManager析构。当然，我们也可以通过将NetWorker::Private声明为QObject的子类来达到这一目的。

instance()函数很简单，我们声明了一个 static 变量，将其指针返回。这是 C++ 单例模式的最简单写法，由于 C++ 标准要求类的构造函数不能被打断，因此这样做也是线程安全的。

.. code-block:: c++

    NetWorker::NetWorker(QObject *parent) :
        QObject(parent),
        d(new NetWorker::Private(this))
    {
        connect(d->manager, &QNetworkAccessManager::finished,
                this, &NetWorker::finished);
    }
     
    NetWorker::~NetWorker()
    {
        delete d;
        d = 0;
    }

构造函数参数列表我们将 d 指针进行赋值。构造函数内容很简单，我们将QNetworkAccessManager的finished()信号进行转发。也就是说，当QNetworkAccessManager发出finished()信号时，NetWorker同样会发出自己的finished()信号。析构函数将 d 指针删除。由于NetWorker::Private是在堆上创建的，并且没有继承QObject，所以我们必须手动调用delete运算符。

.. code-block:: c++

    void NetWorker::get(const QString &url)
    {
        d->manager->get(QNetworkRequest(QUrl(url)));
    }

get()函数也很简单，直接将用户提供的 URL 字符串提供给底层的QNetworkAccessManager，实际上是将操作委托给底层QNetworkAccessManager进行。

现在我们将 QNetworkAccessManager进行了简单的封装。下一章我们开始针对 OpenWeatherMap 的 API 进行编码。
