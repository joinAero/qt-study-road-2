.. _deep_qt5_signals_slots_syntax:

`16. 深入 Qt5 信号槽新语法 <http://www.devbean.net/2012/09/qt-study-road-2-deep-qt5-signals-slots-syntax/>`_
============================================================================================================

:作者: 豆子

:日期: 2012年09月19日

在前面的章节（ :ref:`信号槽 <signal_slot>` 和 :ref:`自定义信号槽 <custom_signal_slot>` ）中，我们详细介绍了有关 Qt 5 的信号槽新语法。由于这次改动很大，许多以前看起来不是问题的问题接踵而来，因此，我们用单独的一章重新介绍一些 Qt 5 的信号槽新语法。


基本用法
--------

Qt 5 引入了信号槽的新语法：使用函数指针能够获得编译期的类型检查。使用我们在自定义信号槽中设计的 Newspaper 类，我们来看看其基本语法：

.. code-block:: c++

	//!!! Qt5
	#include <QObject>
	 
	////////// newspaper.h
	class Newspaper : public QObject
	{
	    Q_OBJECT
	public:
	    Newspaper(const QString & name) :
	        m_name(name)
	    {
	    }
	 
	    void send() const
	    {
	        emit newPaper(m_name);
	    }
	 
	signals:
	    void newPaper(const QString &name);
	 
	private:
	    QString m_name;
	};
	 
	////////// reader.h
	#include <QObject>
	#include <QDebug>
	 
	class Reader : public QObject
	{
	    Q_OBJECT
	public:
	    Reader() {}
	 
	    void receiveNewspaper(cosnt QString & name) const
	    {
	        qDebug() << "Receives Newspaper: " << name;
	    }
	};
	 
	////////// main.cpp
	#include <QCoreApplication>
	 
	#include "newspaper.h"
	#include "reader.h"
	 
	int main(int argc, char *argv[])
	{
	    QCoreApplication app(argc, argv);
	 
	    Newspaper newspaper("Newspaper A");
	    Reader reader;
	    QObject::connect(&newspaper, &Newspaper::newPaper,
	                     &reader,    &Reader::receiveNewspaper);
	    newspaper.send();
	 
	    return app.exec();
	}

在 main() 函数中，我们使用 connect() 函数将 newspaper 对象的 newPaper() 信号与 reader 对象的 receiveNewspaper() 槽函数联系起来。当 newspaper 发出这个信号时，reader 相应的槽函数就会自动被调用。这里我们使用了取址操作符，取到 Newspaper::newPaper() 信号的地址，同样类似的取到了 Reader::receiveNewspaper() 函数地址。编译器能够利用这两个地址，在编译期对这个连接操作进行检查，如果有个任何错误（包括对象没有这个信号，或者信号参数不匹配等），编译时就会发现。

有重载的信号
------------

如果信号有重载，比如我们向 Newspaper 类增加一个新的信号：

.. code-block:: c++

	void newPaper(const QString &name, const QDate &date);

此时如果还是按照前面的写法，编译器会报出一个错误：由于这个函数（注意，信号实际也是一个普通的函数）有重载，因此不能用一个取址操作符获取其地址。回想一下 Qt 4 中的处理。在 Qt 4 中，我们使用 SIGNAL 和 SLOT 两个宏来连接信号槽。如果有一个带有两个参数的信号，像上面那种，那么，我们就可以使用下面的代码：

.. code-block:: c++

	QObject::connect(&newspaper, SIGNAL(newPaper(QString, QDate)),
	                 &reader,    SLOT(receiveNewspaper(QString, QDate)));

注意，我们临时增加了一个 receiveNewspaper() 函数的重载，以便支持两个参数的信号。在 Qt 4 中不存在我们所说的错误，因为 Qt 4 的信号槽连接是带有参数的。因此，Qt 能够自己判断究竟是哪一个信号对应了哪一个槽。

对此，我们也给出了一个解决方案，使用一个函数指针来指明到底是哪一个信号：

.. code-block:: c++

	void (Newspaper:: *newPaperNameDate)(const QString &, const QDate &) = &Newspaper::newPaper;
	QObject::connect(&newspaper, newPaperNameDate,
	                 &reader,    &Reader::receiveNewspaper);

这样，我们使用了函数指针 newspaperNameDate 声明一个带有 QString 和 QDate 两个参数，返回值是 void 的函数，将该函数作为信号，与 Reader::receiveNewspaper() 槽连接起来。这样，我们就回避了之前编译器的错误。归根结底，这个错误是因为函数重载，编译器不知道要取哪一个函数的地址，而我们显式指明一个函数就可以了。

如果你觉得这种写法很难看，想像前面一样写成一行，当然也是由解决方法的：

.. code-block:: c++

	QObject::connect(&newspaper,
	                 (void (Newspaper:: *)(const QString &, const QDate &))&Newspaper::newPaper,
	                 &reader,
	                 &Reader::receiveNewspaper);

这是一种换汤不换药的做法：我们只是声明了一个匿名的函数指针，而之前我们的函数指针是有名字的。不过，我们并不推荐这样写，而是希望以下的写法：

.. code-block:: c++

	QObject::connect(&newspaper,
	                 static_cast<void (Newspaper:: *)(const QString &, const QDate &)>(&Newspaper::newPaper),
	                 &reader,
	                 &Reader::receiveNewspaper);

对比上面两种写法。第一个使用的是 C 风格的强制类型转换。此时，如果你改变了信号的类型，那么你就会有一个潜在的运行时错误。例如，如果我们把 (const QString &, const QDate &) 两个参数修改成 (const QDate &, const QString &)，C 风格的强制类型转换就会失败，并且这个错误只能在运行时发现。而第二种则是 C++ 推荐的风格，当参数类型改变时，编译器会检测到这个错误。

注意，这里我们只是强调了函数参数的问题。如果前面的对象都错了呢？比如，我们写的 newspaper 对象并不是一个 Newspaper，而是 Newspaper2？此时，编译器会直接失败，因为 connect() 函数会去寻找 sender->*signal，如果这两个参数不满足，则会直接报错。

带有默认参数的槽函数
--------------------

Qt 允许信号和槽的参数数目不一致：槽函数的参数数目要比信号的参数少。这是因为，我们信号的参数实际是作为一种返回值。正如普通的函数调用一样，我们可以选择忽略函数返回值，但是不能使用一个并不存在的返回值。如果槽函数的参数数目比信号的多，在槽函数中就使用到这些参数的时候，实际这些参数并不存在（因为信号的参数比槽的少，因此并没有传过来），函数就会报错。这种情况往往有两个原因：一是槽的参数就是比信号的少，此时我们可以像前面那种写法直接连接。另外一个原因是，信号的参数带有默认值。比如

.. code-block:: c++

	void QPushButton::clicked(bool checked = false)

就是这种情况。

然而，有一种情况，槽函数的参数可以比信号的多，那就是槽函数的参数带有默认值。比如，我们的 Newspaper 和 Reader 有下面的代码：

.. code-block:: c++

	// Newspaper
	signals:
	    void newPaper(const QString &name);
	// Reader
	    void receiveNewspaper(const QString &name, const QDate &date = QDate::currentDate());

虽然 Reader::receiveNewspaper() 的参数数目比 Newspaper::newPaper() 多，但是由于 Reader::receiveNewspaper() 后面一个参数带有默认值，所以该参数不是必须提供的。但是，如果你按照前面的写法，比如如下的代码：

.. code-block:: c++

	QObject::connect(&newspaper,
	                 static_cast<void (Newspaper:: *)(const QString &)>(&Newspaper::newPaper),
	                 &reader,
	                 static_cast<void (Reader:: *)(const QString &, const QDate & =QDate::currentDate())>(&Reader::receiveNewspaper));

你会得到一个断言错误：

.. code-block:: none

	The slot requires more arguments than the signal provides.

我们不能在函数指针中使用函数参数的默认值。这是 C++ 语言的限制： **参数默认值只能使用在直接地函数调用中。当使用函数指针取其地址的时候，默认参数是不可见的！**

当然，此时你可以选择 Qt 4 的连接语法。如果你还是想使用 Qt 5 的新语法，目前的办法只有一个：Lambda 表达式。不要担心你的编译器不支持 Lambda 表达式，因为在你使用 Qt 5 的时候，能够支持 Qt 5 的编译器都是支持 Lambda 表达式的。于是，我们的代码就变成了：

.. code-block:: c++

	QObject::connect(&newspaper,
	                 static_cast<void (Newspaper:: *)(const QString &)>(&Newspaper::newPaper),
	                 [=](const QString &name) { /* Your code here. */ });
