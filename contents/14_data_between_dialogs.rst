.. _data_between_dialogs:

`14. 对话框数据传递 <http://www.devbean.net/2012/09/qt-study-road-2-data-between-dialogs/>`_
============================================================================================

:作者: 豆子

:日期: 2012年09月15日

对话框的出现用于完成一个简单的或者是短期的任务。对话框与主窗口之间的数据交互相当重要。本节将讲解如何在对话框和主窗口之间进行数据交互。按照前文的讲解，对话框分为模态和非模态两种。我们也将以这两种为例，分别进行阐述。


模态对话框使用了 exec() 函数将其显示出来。exec() 函数的真正含义是开启一个新的事件循环（我们会在后面的章节中详细介绍有关事件的概念）。所谓事件循环，可以理解成一个无限循环。Qt 在开启了事件循环之后，系统发出的各种事件才能够被程序监听到。这个事件循环相当于一种轮询的作用。既然是无限循环，当然在开启了事件循环的地方，代码就会被阻塞，后面的语句也就不会被执行到。因此，对于使用了 exec() 显示的模态对话框，我们可以在 exec() 函数之后直接从对话框的对象获取到数据值。

看一下下面的代码：

.. code-block:: c++

	void MainWindow::open()
	{
	    QDialog dialog(this);
	    dialog.setWindowTitle(tr("Hello, dialog!"));
	    dialog.exec();
	    qDebug() << dialog.result();
	}

上面的代码中，我们使用 exec() 显示一个模态对话框。最后一行代码，qDebug() 类似于 std::cout 或者 Java 的 System.out.println(); 语句，将后面的信息输出到标准输出，一般就是控制台。使用 qDebug() 需要引入头文件。在 exec() 函数之后，我们直接可以获取到 dialog 的数据值。注意，exec() 开始了一个事件循环，代码被阻塞到这里。由于 exec() 函数没有返回，因此下面的 result() 函数也就不会被执行。直到对话框关闭，exec() 函数返回，此时，我们就可以取得对话框的数据。

需要注意的一点是，如果我们设置 dialog 的属性为 WA_DeleteOnClose，那么当对话框关闭时，对象被销毁，我们就不能使用这种办法获取数据了。在这种情况下，我们可以考虑使用 parent 指针的方式构建对话框，避免设置 WA_DeleteOnClose 属性；或者是利用另外的方式。

实际上，QDialog::exec() 是有返回值的，其返回值是 QDialog::Accepted 或者 QDialog::Rejected。一般我们会使用类似下面的代码：

.. code-block:: c++

	QDialog dialog(this);
	if (dialog.exec() == QDialog::Accepted) {
	    // do something
	} else {
	    // do something else
	}

来判断对话框的返回值，也就是用户是点击了“确定”还是“取消”。更多细节请参考 QDialog 文档。

模态对话框相对简单，如果是非模态对话框，QDialog::show() 函数会立即返回，如果我们也这么写，就不可能取得用户输入的数据。因为 show() 函数不会阻塞主线程，show() 立即返回，用户还没有来得及输入，就要执行后面的代码，当然是不会有正确结果的。那么我们就应该换一种思路获取数据，那就是使用信号槽机制。

由于非模态对话框在关闭时可以调用 QDialog::accept() 或者 QDialog::reject() 或者更通用的 QDialog::done() 函数，所以我们可以在这里发出信号。另外，如果找不到合适的信号发出点，我们可以重写 QDialog::closeEvent() 函数，在这里发出信号。在需要接收数据的窗口（这里是主窗口）连接到这个信号即可。类似的代码片段如下所示：

.. code-block:: c++

	//!!! Qt 5
	// in dialog:
	void UserAgeDialog::accept()
	{
	    emit userAgeChanged(newAge); // newAge is an int
	    QDialog::accept();
	}
	 
	// in main window:
	void MainWindow::showUserAgeDialog()
	{
	    UserAgeDialog *dialog = new UserAgeDialog(this);
	    connect(dialog, &UserAgeDialog::userAgeChanged, this, &MainWindow::setUserAge);
	    dialog->show();
	}
	 
	// ...
	 
	void MainWindow::setUserAge(int age)
	{
	    userAge = age;
	}

上面的代码很简单，这里不再赘述。另外，上述代码的 Qt 4 版本也应该可以很容易地实现。

不要担心如果对话框关闭，是不是还能获取到数据。因为 Qt 信号槽的机制保证，在槽函数在调用的时候，我们始终可以使用 sender() 函数获取到 signal 的发出者。关于 sender() 函数，可以在文档中找到更多的介绍。顺便说一句，sender() 函数的存在使我们可以利用这个函数，来实现一个只能打开一个的非模态对话框（方法就是在对话框打开时在一个对话框映射表中记录下标记，在对话框关闭时利用 sender() 函数判断是不是该对话框，然后从映射表中将其删除）。
