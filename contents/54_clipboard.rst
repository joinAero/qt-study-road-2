.. _clipboard:

`54. 剪贴板 <http://www.devbean.net/2013/06/qt-study-road-2-clipboard/>`_
=========================================================================

:作者: 豆子

:日期: 2013年06月08日

剪贴板的操作经常和前面所说的拖放技术在一起使用。大家对剪贴板都很熟悉。我们可以简单地把它理解成一个数据存储池，外面的数据可以存进去，里面数据也可以取出来。剪贴板是由操作系统维护的，所以这提供了跨应用程序的数据交互的一种方式。Qt 已经为我们封装好很多关于剪贴板的操作，我们可以在自己的应用中很容易实现对剪贴板的支持，代码实现起来也是很简单的：

.. code-block:: c++

    class ClipboardDemo : public QWidget
    {
        Q_OBJECT
    public:
        ClipboardDemo(QWidget *parent = 0);
    private slots:
        void setClipboardContent();
        void getClipboardContent();
    };

我们定义了一个 ClipboardDemo 类。这个类只有两个槽函数，一个是从剪贴板获取内容，一个是给剪贴板设置内容。

.. code-block:: c++

    ClipboardDemo::ClipboardDemo(QWidget *parent)
        : QWidget(parent)
    {
        QVBoxLayout *mainLayout = new QVBoxLayout(this);
        QHBoxLayout *northLayout = new QHBoxLayout;
        QHBoxLayout *southLayout = new QHBoxLayout;
     
        QTextEdit *editor = new QTextEdit;
        QLabel *label = new QLabel;
        label->setText("Text Input: ");
        label->setBuddy(editor);
        QPushButton *copyButton = new QPushButton;
        copyButton->setText("Set Clipboard");
        QPushButton *pasteButton = new QPushButton;
        pasteButton->setText("Get Clipboard");
     
        northLayout->addWidget(label);
        northLayout->addWidget(editor);
        southLayout->addWidget(copyButton);
        southLayout->addWidget(pasteButton);
        mainLayout->addLayout(northLayout);
        mainLayout->addLayout(southLayout);
     
        connect(copyButton, SIGNAL(clicked()), this, SLOT(setClipboard()));
        connect(pasteButton, SIGNAL(clicked()), this, SLOT(getClipboard()));
    }

主界面也很简单：程序分为上下两行，上一行显示一个文本框，下一行是两个按钮，分别为设置剪贴板和读取剪贴板。最主要的代码还是在两个槽函数中：

.. code-block:: c++

    void ClipboardDemo::setClipboard()
    {
        QClipboard *board = QApplication::clipboard();
        board->setText("Text from Qt Application");
    }
     
    void ClipboardDemo::getClipboard()
    {
        QClipboard *board = QApplication::clipboard();
        QString str = board->text();
        QMessageBox::information(NULL, "From clipboard", str);
    }

槽函数也很简单。我们使用 QApplication::clipboard() 函数获得系统剪贴板对象。这个函数的返回值是 QClipboard 指针。我们可以从这个类的 API 中看到，通过 setText()，setImage() 或者 setPixmap() 函数可以将数据放置到剪贴板内，也就是通常所说的剪贴或者复制的操作；使用 text()，image() 或者 pixmap() 函数则可以从剪贴板获得数据，也就是粘贴。

另外值得说的是，通过上面的例子可以看出，QTextEdit 默认就支持 Ctrl+C, Ctrl+V 等快捷键操作的。不仅如此，很多 Qt 的组件都提供了很方便的操作，因此我们需要从文档中获取具体的信息，从而避免自己重新去发明轮子。

QClipboard 提供的数据类型很少，如果需要，我们可以继承 QMimeData 类，通过调用 setMimeData() 函数让剪贴板能够支持我们自己的数据类型。具体实现我们已经在前面的章节中有过介绍，这里不再赘述。

在 X11 系统中，鼠标中键（一般是滚轮）可以支持剪贴操作。为了实现这一功能，我们需要向 QClipboard::text() 函数传递 QClipboard::Selection 参数。例如，我们在鼠标按键释放的事件中进行如下处理：

.. code-block:: c++

    void MyTextEditor::mouseReleaseEvent(QMouseEvent *event)
    {
        QClipboard *clipboard = QApplication::clipboard();
        if (event->button() == Qt::MidButton
                && clipboard->supportsSelection()) {
            QString text = clipboard->text(QClipboard::Selection);
            pasteText(text);
        }
    }

这里的 supportsSelection() 函数在 X11 平台返回 true，其余平台都是返回 false。这样，我们便可以为 X11 平台提供额外的操作。

另外，QClipboard 提供了 dataChanged() 信号，以便监听剪贴板数据变化。