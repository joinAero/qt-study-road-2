.. _events_accept_reject:

`19. 事件的接受与忽略 <http://www.devbean.net/2012/09/qt-study-road-2-events-accept-reject/>`_
==============================================================================================

:作者: 豆子

:日期: 2012年09月29日

上一章我们介绍了有关事件的相关内容。我们曾经提到，事件可以依情况接受和忽略。现在，我们就来了解下有关事件的更多的知识。


首先来看一段代码：

.. code-block:: c++

	//!!! Qt5
	// ---------- custombutton.h ---------- //
	class CustomButton : public QPushButton
	{
	    Q_OBJECT
	public:
	    CustomButton(QWidget *parent = 0);
	private:
	    void onButtonCliecked();
	};
	 
	// ---------- custombutton.cpp ---------- //
	CustomButton::CustomButton(QWidget *parent) :
	    QPushButton(parent)
	{
	    connect(this, &CustomButton::clicked,
	            this, &CustomButton::onButtonCliecked);
	}
	 
	void CustomButton::onButtonCliecked()
	{
	    qDebug() << "You clicked this!";
	}
	 
	// ---------- main.cpp ---------- //
	int main(int argc, char *argv[])
	{
	    QApplication a(argc, argv);
	 
	    CustomButton btn;
	    btn.setText("This is a Button!");
	    btn.show();
	 
	    return a.exec();
	}

这是一段简单的代码，经过我们前面一段时间的学习，我们已经能够知道这段代码的运行结果：点击按钮，会在控制台打印出“You clicked this!”字符串。这是我们前面介绍过的内容。下面，我们向 CustomButton 类添加一个事件函数：

.. code-block:: c++

	// CustomButton
	...
	protected:
	    void mousePressEvent(QMouseEvent *event);
	...
	 
	// ---------- custombutton.cpp ---------- //
	...
	void CustomButton::mousePressEvent(QMouseEvent *event)
	{
	    if (event->button() == Qt::LeftButton) {
	        qDebug() << "left";
	    } else {
	        QPushButton::mousePressEvent(event);
	    }
	}
	...

我们重写了 CustomButton 的 mousePressEvent() 函数，也就是鼠标按下。在这个函数中，我们判断如果鼠标按下的是左键，则打印出来“left”字符串，否则，调用父类的同名函数。编译运行这段代码，当我们点击按钮时，“You clicked this!”字符串不再出现，只有一个“left”。也就是说，我们把父类的实现覆盖掉了。由此可以看出，父类 QPushButton 的 mousePressEvent() 函数中肯定发出了 clicked() 信号，否则的话，我们的槽函数怎么会不执行了呢？这暗示我们一个非常重要的细节： **当重写事件回调函数时，时刻注意是否需要通过调用父类的同名函数来确保原有实现仍能进行！** 比如我们的 CustomButton 了，如果像我们这么覆盖函数，clicked() 信号永远不会发生，你连接到这个信号的槽函数也就永远不会被执行。这个错误非常隐蔽，很可能会浪费你很多时间才能找到。因为这个错误不会有任何提示。这一定程度上说，我们的组件“忽略”了父类的事件，但这更多的是一种违心之举，一种错误。

通过调用父类的同名函数，我们可以把 Qt 的事件传递看成链状：如果子类没有处理这个事件，就会继续向其父类传递。Qt 的事件对象有两个函数：accept() 和 ignore()。正如它们的名字一样，前者用来告诉 Qt，这个类的事件处理函数想要这个事件；后者则告诉 Qt，这个类的事件处理函数不想要这个事件。无论是 accept() 还是 ignore()，该类 **不想要的事件** 都会被继续发送给其父组件。在事件处理函数中，可以使用 isAccepted() 来查询这个事件是不是已经被接收了。

事实上，我们很少会使用 accept() 和 ignore() 函数，而是像上面的示例一样，如果希望忽略事件（所谓忽略，是指自己不想要这个事件），只要调用父类的响应函数即可。记得我们曾经说过，Qt 中的事件都是 protected 的，因此，重写的函数必定存在着其父类中的响应函数，所以，这个方法是可行的。为什么要这么做，而不是自己去手动调用这两个函数呢？因为我们无法确认父类中的这个处理函数有没有额外的操作。如果我们在子类中直接忽略事件，Qt 将不会再去寻找其他的接收者，那么父类的操作也就不能进行，这可能会有潜在的危险。

要理解这一点，我们可以查看一下 QWidget 的 mousePressEvent() 函数的实现：

.. code-block:: c++

	//!!! Qt5
	void QWidget::mousePressEvent(QMouseEvent *event)
	{
	    event->ignore();
	    if ((windowType() == Qt::Popup)) {
	        event->accept();
	        QWidget* w;
	        while ((w = QApplication::activePopupWidget()) && w != this){
	            w->close();
	            if (QApplication::activePopupWidget() == w)
	                w->hide(); // hide at least
	        }
	        if (!rect().contains(event->pos())){
	            close();
	        }
	    }
	}

这段代码在 Qt4 和 Qt5 中基本一致（区别在于 activePopupWidget() 一行，Qt4 的版本是 qApp->activePopupWidget()）。注意函数的第一个语句：event->ignore();，如果子类都没有重写这个函数，Qt 会默认忽略这个事件，不会继续传播。如果我们在子类的 mousePressEvent() 函数中直接调用了 accept() 或者 ignore()，而没有调用父类的同名函数，QWidget::mousePressEvent() 函数中关于 Popup 判断的那段代码就不会被执行，因此可能会出现默认其妙的怪异现象。

不过，事情也不是绝对的。在一个情形下，我们必须使用 accept() 和 ignore() 函数，那就是窗口关闭的事件。回到我们前面写的简单的文本编辑器。我们在构造函数中添加如下代码：

.. code-block:: c++

	//!!! Qt5
	...
	textEdit = new QTextEdit(this);
	setCentralWidget(textEdit);
	connect(textEdit, &QTextEdit::textChanged, [=]() {
	    this->setWindowModified(true);
	});
	 
	setWindowTitle("TextPad [*]");
	...
	 
	void MainWindow::closeEvent(QCloseEvent *event)
	{
	    if (isWindowModified()) {
	        bool exit = QMessageBox::question(this,
	                                      tr("Quit"),
	                                      tr("Are you sure to quit this application?"),
	                                      QMessageBox::Yes | QMessageBox::No,
	                                      QMessageBox::No) == QMessageBox::Yes;
	        if (exit) {
	            event->accept();
	        } else {
	            event->ignore();
	        }
	    } else {
	        event->accept();
	    }
	}

setWindowTitle() 函数可以使用 [\*] 这种语法来表明，在窗口内容发生改变时（通过 setWindowModified(true) 函数通知），Qt 会自动在标题上面的 [\*] 位置替换成 \* 号。我们使用 Lambda 表达式连接 QTextEdit::textChanged() 信号，将 windowModified 设置为 true。然后我们需要重写 closeEvent() 函数。在这个函数中，我们首先判断是不是有过修改，如果有，则弹出询问框，问一下是否要退出。如果用户点击了“Yes”，则接受关闭事件，这个事件所在的操作就是关闭窗口。因此，一旦接受事件，窗口就会被关闭；否则窗口继续保留。当然，如果窗口内容没有被修改，则直接接受事件，关闭窗口。
