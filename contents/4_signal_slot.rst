.. _signal_slot:

`4. 信号槽 <http://www.devbean.net/2012/08/qt-study-road-2-signal-slot/>`_
==========================================================================

:作者: 豆子

:日期: 2012年08月23日

信号槽是 Qt 框架引以为豪的机制之一。熟练使用和理解信号槽，能够设计出解耦的非常漂亮的程序，有利于增强我们的技术设计能力。

所谓信号槽，实际就是观察者模式。当某个事件发生之后，比如，按钮检测到自己被点击了一下，它就会发出一个信号（signal）。这种发出是没有目的的，类似广播。如果有对象对这个信号感兴趣，它就会使用连接（connect）函数，意思是，用自己的一个函数（成为槽（slot））来处理这个信号。也就是说，当信号发出时，被连接的槽函数会自动被回调。这就类似观察者模式：当发生了感兴趣的事件，某一个操作就会被自动触发。*（这里提一句，Qt 的信号槽使用了额外的处理来实现，并不是 GoF 经典的观察者模式的实现方式。）*


为了体验一下信号槽的使用，我们以一段简单的代码说明：

.. code-block:: c++

	// !!! Qt 5
	#include <QApplication>
	#include <QPushButton>
	 
	int main(int argc, char *argv[])
	{
	    QApplication app(argc, argv);
	 
	    QPushButton button("Quit");
	    QObject::connect(&button, &QPushButton::clicked, &QApplication::quit);
	    button.show();
	 
	    return app.exec();
	}

这里再次强调，我们的代码是以 Qt 5 为主线，这意味着，有的代码放在 Qt 4 上是不能编译的。因此，豆子会在每一段代码的第一行添加注释，用以表明该段代码是使用 Qt 5 还是 Qt 4 进行编译。读者在测试代码的时候，需要自行选择相应的 Qt 版本。

我们按照前面文章中介绍的在 Qt Creator 中创建工程的方法创建好工程，然后将 main() 函数修改为上面的代码。点击运行，我们会看到一个按钮，上面有“Quit”字样。点击按钮，程序退出。

按钮在 Qt 中被称为 QPushButton。对它的创建和显示，同前文类似，这里不做过多的讲解。我们这里要仔细分析 QObject::connect() 这个函数。

在 Qt 5 中，QObject::connect() 有五个重载：

.. code-block:: c++

	QMetaObject::Connection connect(const QObject *, const char *,
	                                const QObject *, const char *,
	                                Qt::ConnectionType);
	 
	QMetaObject::Connection connect(const QObject *, const QMetaMethod &,
	                                const QObject *, const QMetaMethod &,
	                                Qt::ConnectionType);
	 
	QMetaObject::Connection connect(const QObject *, const char *,
	                                const char *,
	                                Qt::ConnectionType) const;
	 
	QMetaObject::Connection connect(const QObject *, PointerToMemberFunction,
	                                const QObject *, PointerToMemberFunction,
	                                Qt::ConnectionType)
	 
	QMetaObject::Connection connect(const QObject *, PointerToMemberFunction,
	                                Functor);

这五个重载的返回值都是 QMetaObject::Connection，现在我们不去关心这个返回值。下面我们先来看看 connect() 函数最常用的一般形式：

.. code-block:: c++

	// !!! Qt 5
	connect(sender,   signal,
	        receiver, slot);

这是我们最常用的形式。connect() 一般会使用前面四个参数，第一个是发出信号的对象，第二个是发送对象发出的信号，第三个是接收信号的对象，第四个是接收对象在接收到信号之后所需要调用的函数。也就是说，当 sender 发出了 signal 信号之后，会自动调用 receiver 的 slot 函数。

这是最常用的形式，我们可以套用这个形式去分析上面给出的五个重载。第一个，sender 类型是 const QObject \*，signal 的类型是 const char \*，receiver 类型是 const QObject \*，slot 类型是 const char \*。这个函数将 signal 和 slot 作为字符串处理。第二个，sender 和 receiver 同样是 const QObject \*，但是 signal 和 slot 都是 const QMetaMethod &。我们可以将每个函数看做是 QMetaMethod 的子类。因此，这种写法可以使用 QMetaMethod 进行类型比对。第三个，sender 同样是 const QObject \*，signal 和 slot 同样是 const char \*，但是却缺少了 receiver。这个函数其实是将 this 指针作为 receiver。第四个，sender 和 receiver 也都存在，都是 const QObject \*，但是 signal 和 slot 类型则是 PointerToMemberFunction。看这个名字就应该知道，这是指向成员函数的指针。第五个，前面两个参数没有什么不同，最后一个参数是 Functor 类型。这个类型可以接受 static 函数、全局函数以及 Lambda 表达式。

由此我们可以看出，connect() 函数，sender 和 receiver 没有什么区别，都是 QObject 指针；主要是 signal 和 slot 形式的区别。具体到我们的示例，我们的 connect() 函数显然是使用的第五个重载，最后一个参数是 QApplication 的 static 函数 quit()。也就是说，当我们的 button 发出了 clicked() 信号时，会调用 QApplication 的 quit() 函数，使程序退出。

信号槽要求信号和槽的参数一致，所谓一致，是参数类型一致。如果不一致，允许的情况是，槽函数的参数可以比信号的少，即便如此，槽函数存在的那些参数的顺序也必须和信号的前面几个一致起来。这是因为，你可以在槽函数中选择忽略信号传来的数据（也就是槽函数的参数比信号的少），但是不能说信号根本没有这个数据，你就要在槽函数中使用（就是槽函数的参数比信号的多，这是不允许的）。

如果信号槽不符合，或者根本找不到这个信号或者槽函数的话，比如我们改成：

.. code-block:: c++

	QObject::connect(&button, &QPushButton::clicked, &QApplication::quit2);

由于 QApplication 没有 quit2 这样的函数的，因此在编译时，会有编译错误：

``'quit2' is not a member of QApplication``

这样，使用成员函数指针，我们就不会担心在编写信号槽的时候会出现函数错误。

借助 Qt 5 的信号槽语法，我们可以将一个对象的信号连接到 Lambda 表达式，例如：

.. code-block:: c++

	// !!! Qt 5
	#include <QApplication>
	#include <QPushButton>
	#include <QDebug>
	 
	int main(int argc, char *argv[])
	{
	    QApplication app(argc, argv);
	 
	    QPushButton button("Quit");
	    QObject::connect(&button, &QPushButton::clicked, [](bool) {
	        qDebug() << "You clicked me!";
	    });
	    button.show();
	 
	    return app.exec();
	}

注意这里的 Lambda 表达式接收一个 bool 参数，这是因为 QPushButton 的 clicked() 信号实际上是有一个参数的。Lambda 表达式中的 qDebug() 类似于 cout，将后面的字符串打印到标准输出。如果要编译上面的代码，你需要在 pro 文件中添加这么一句：

``QMAKE_CXXFLAGS += -std=c++0x``

然后正常编译即可。

Qt 4 的信号槽同 Qt 5 类似。在 Qt 4 的 QObject 中，有三个不同的 connect() 重载：

.. code-block:: c++

	bool connect(const QObject *, const char *,
	             const QObject *, const char *,
	             Qt::ConnectionType);
	 
	bool connect(const QObject *, const QMetaMethod &,
	             const QObject *, const QMetaMethod &,
	             Qt::ConnectionType);
	 
	bool connect(const QObject *, const char *,
	             const char *,
	             Qt::ConnectionType) const

除了返回值，Qt 4 的 connect() 函数与 Qt 5 最大的区别在于，Qt 4 的 signal 和 slot 只有 const char * 这么一种形式。如果我们将上面的代码修改为 Qt 4 的，则应该是这样的：

.. code-block:: c++

	// !!! Qt 4
	#include <QApplication>
	#include <QPushButton>
	 
	int main(int argc, char *argv[])
	{
	    QApplication app(argc, argv);
	 
	    QPushButton button("Quit");
	    QObject::connect(&button, SIGNAL(clicked()),
	                     &app,    SLOT(quit()));
	    button.show();
	 
	    return app.exec();
	}

我们使用了 SIGNAL 和 SLOT 这两个宏，将两个函数名转换成了字符串。注意，即使 quit() 是 QApplication 的 static 函数，也必须传入一个对象指针。这也是 Qt 4 的信号槽语法的局限之处。另外，注意到 connect() 函数的 signal 和 slot 都是接受字符串，因此，不能将全局函数或者 Lambda 表达式传入 connect()。一旦出现连接不成功的情况，Qt 4 是没有编译错误的（因为一切都是字符串，编译期是不检查字符串是否匹配），而是在运行时给出错误。这无疑会增加程序的不稳定性。

信号槽机制是 Qt 的最大特性之一。这次我们只是初略了解了信号槽，知道了如何使用 connect() 函数进行信号槽的连接。在后面的内容中，我们将进一步介绍信号槽，了解如何设计自己的信号槽等等。
