.. _custom_signal_slot:

`5. 自定义信号槽 <http://www.devbean.net/2012/08/qt-study-road-2-custom-signal-slot/>`_
=======================================================================================

:作者: 豆子

:日期: 2012年08月24日

上一节我们详细分析了 connect() 函数。使用 connect() 可以让我们连接系统提供的信号和槽。但是，Qt 的信号槽机制并不仅仅是使用系统提供的那部分，还会允许我们自己设计自己的信号和槽。这也是 Qt 框架的设计思路之一，用于我们设计解耦的程序。本节将讲解如何在自己的程序中自定义信号槽。

信号槽不是 GUI 模块提供的，而是 Qt 核心特性之一。因此，我们可以在普通的控制台程序使用信号槽。


经典的观察者模式在讲解举例的时候通常会举报纸和订阅者的例子。有一个报纸类 Newspaper，有一个订阅者类 Subscriber。Subscriber 可以订阅 Newspaper。这样，当 Newspaper 有了新的内容的时候，Subscriber 可以立即得到通知。在这个例子中，观察者是 Subscriber，被观察者是 Newspaper。在经典的实现代码中，观察者会将自身注册到被观察者的一个容器中（比如 subscriber.registerTo(newspaper)）。被观察者发生了任何变化的时候，会主动遍历这个容器，依次通知各个观察者（newspaper.notifyAllSubscribers()）。

下面我们看看使用 Qt 的信号槽，如何实现上述观察者模式。注意，这里我们仅仅是使用这个案例，我们的代码并不是去实现一个经典的观察者模式。也就是说，我们使用 Qt 的信号槽机制来获得同样的效果。

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
	 
	    void send()
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
	 
	    void receiveNewspaper(const QString & name)
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

当我们运行上面的程序时，会看到终端输出 Receives Newspaper: Newspaper A 这样的字样。

下面我们来分析下自定义信号槽的代码。

这段代码放在了三个文件，分别是 newspaper.h，reader.h 和 main.cpp。为了减少文件数量，可以把 newspaper.h 和 reader.h 都放在 main.cpp 的 main() 函数之前吗？答案是，可以，但是需要有额外的操作。具体问题，我们在下面会详细说明。

首先看 Newspaper 这个类。这个类继承了 QObject 类。只有继承了 QObject 类的类，才具有信号槽的能力。所以，为了使用信号槽，必须继承 QObject。凡是 QObject 类（不管是直接子类还是间接子类），都应该在第一行代码写上 Q_OBJECT。不管是不是使用信号槽，都应该添加这个宏。这个宏的展开将为我们的类提供信号槽机制、国际化机制以及 Qt 提供的不基于 C++ RTTI 的反射能力。因此，如果你觉得你的类不需要使用信号槽，就不添加这个宏，就是错误的。其它很多操作都会依赖于这个宏。注意，这个宏将由 moc（我们会在后面章节中介绍 moc。这里你可以将其理解为一种预处理器，是比 C++ 预处理器更早执行的预处理器。） 做特殊处理，不仅仅是宏展开这么简单。moc 会读取标记了 Q_OBJECT 的 **头文件** ，生成以 moc\_ 为前缀的文件，比如 newspaper.h 将生成 moc_newspaper.h。你可以到构建目录查看这个文件，看看到底增加了什么内容。注意，由于 moc 只处理头文件中的标记了 Q_OBJECT 的类声明，不会处理 cpp 文件中的类似声明。因此，如果我们的 Newspaper 和 Reader 类位于 main.cpp 中，是无法得到 moc 的处理的。解决方法是，我们手动调用 moc 工具处理 main.cpp，并且将 main.cpp 中的 include “newspaper.h” 改为 include “moc_newspaper.h” 就可以了。不过，这是相当繁琐的步骤，为了避免这样修改，我们还是将其放在头文件中。许多初学者会遇到莫名其妙的错误，一加上 Q_OBJECT 就出错，很大一部分是因为没有注意到这个宏应该放在头文件中。

Newspaper 类的 public 和 private 代码块都比较简单，只不过它新加了一个 signals。signals 块所列出的，就是该类的信号。信号就是一个个的函数名，返回值是 void（因为无法获得信号的返回值，所以也就无需返回任何值），参数是该类需要让外界知道的数据。信号作为函数名，不需要在 cpp 函数中添加任何实现*（我们曾经说过，Qt 程序能够使用普通的 make 进行编译。没有实现的函数名怎么会通过编译？原因还是在 moc，moc 会帮我们实现信号函数所需要的函数体，所以说，moc 并不是单纯的将 Q_OBJECT 展开，而是做了很多额外的操作）* 。

Newspaper 类的 send() 函数比较简单，只有一个语句 emit newPaper(m_name);。emit 是 Qt 对 C++ 的扩展，是一个关键字（其实也是一个宏）。emit 的含义是发出，也就是发出 newPaper() 信号。感兴趣的接收者会关注这个信号，可能还需要知道是哪份报纸发出的信号？所以，我们将实际的报纸名字 m_name 当做参数传给这个信号。当接收者连接这个信号时，就可以通过槽函数获得实际值。这样就完成了数据从发出者到接收者的一个转移。

Reader 类更简单。因为这个类需要接受信号，所以我们将其继承了 QObject，并且添加了 Q_OBJECT 宏。后面则是默认构造函数和一个普通的成员函数。Qt 5 中，任何成员函数、static 函数、全局函数和 Lambda 表达式都可以作为槽函数。与信号函数不同，槽函数必须自己完成实现代码。槽函数就是普通的成员函数，因此也会受到 public、private 等访问控制符的影响。*（我们没有说信号也会受此影响，事实上，如果信号是 private 的，这个信号就不能在类的外面连接，也就没有任何意义。）*

main() 函数中，我们首先创建了 Newspaper 和 Reader 两个对象，然后使用 QObject::connect() 函数。这个函数我们上一节已经详细介绍过，这里应该能够看出这个连接的含义。然后我们调用 Newspaper 的 send() 函数。这个函数只有一个语句：发出信号。由于我们的连接，当这个信号发出时，自动调用 reader 的槽函数，打印出语句。

这样我们的示例程序讲解完毕。我们基于 Qt 的信号槽机制，不需要观察者的容器，不需要注册对象，就实现了观察者模式。

下面总结一下自定义信号槽需要注意的事项：

* 发送者和接收者都需要是 QObject 的子类（当然，槽函数是全局函数、Lambda 表达式等无需接收者的时候除外）；
* 使用 signals 标记信号函数，信号是一个函数声明，返回 void，不需要实现函数代码；
* 槽函数是普通的成员函数，会受到 public、private、protected 的影响；
* 使用 emit 在恰当的位置发送信号；
* 使用 QObject::connect() 函数连接信号和槽。

Qt 4

下面给出 Qt 4 中相应的代码：

.. code-block:: c++

	//!!! Qt4
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
	    void newPaper(const QString &name) const;
	 
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
	 
	public slots:
	    void receiveNewspaper(const QString & name) const
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
	    QObject::connect(&newspaper, SIGNAL(newPaper(QString)),
	                     &reader,    SLOT(receiveNewspaper(QString)));
	    newspaper.send();
	 
	    return app.exec();
	}

注意下 Qt 4 与 Qt 5 的区别。

Newspaper 类没有什么区别。

Reader 类，receiveNewspaper() 函数放在了 public slots 块中。在 Qt 4 中，槽函数必须放在由 slots 修饰的代码块中，并且要使用访问控制符进行访问控制。其原则同其它函数一样：默认是 private 的，如果要在外部访问，就应该是 public slots；如果只需要在子类访问，就应该是 protected slots。

main() 函数中，QObject::connect() 函数，第二、第四个参数需要使用 SIGNAL 和 SLOT 这两个宏转换成字符串（具体事宜我们在上一节介绍过）。注意 SIGNAL 和 SLOT 的宏参数并不是取函数指针，而是除去返回值的函数声明，并且 const 这种参数修饰符是忽略不计的。
