.. _dnd:

`52. 使用拖放 <http://www.devbean.net/2013/05/qt-study-road-2-dnd/>`_
=========================================================================================

:作者: 豆子

:日期: 2013年05月21日

拖放（Drag and Drop），通常会简称为 DnD，是现代软件开发中必不可少的一项技术。它提供了一种能够在应用程序内部甚至是应用程序之间进行信息交换的机制。操作系统与应用程序之间进行的剪贴板内容的交换，也可以被认为是拖放的一部分。


拖放其实是由两部分组成的：拖动和释放。拖动是将被拖放对象进行移动，释放是将被拖放对象放下。前者是一个按下鼠标按键并移动的过程，后者是一个松开鼠标按键的过程；通常这两个操作之间的鼠标按键是被一直按下的。当然，这只是一种普遍的情况，其它情况还是要看应用程序的具体实现。对于 Qt 而言，一个组件既可以作为被拖动对象进行拖动，也可以作为释放掉的目的地对象，或者二者都是。

在下面的例子中（来自 C++ GUI Programming with Qt4, 2nd Edition），我们将创建一个程序，将操作系统中的文本文件拖进来，然后在窗口中读取内容。

.. code-block:: c++

    class MainWindow : public QMainWindow
    {
        Q_OBJECT
    public:
        MainWindow(QWidget *parent = 0);
        ~MainWindow();
    protected:
        void dragEnterEvent(QDragEnterEvent *event);
        void dropEvent(QDropEvent *event);
    private:
        bool readFile(const QString &fileName);
        QTextEdit *textEdit;
    };

注意到我们需要重写 dragEnterEvent() 和 dropEvent() 两个函数。顾名思义，前者是拖放进入的事件，后者是释放鼠标的事件。

.. code-block:: c++

    MainWindow::MainWindow(QWidget *parent)
        : QMainWindow(parent)
    {
        textEdit = new QTextEdit;
        setCentralWidget(textEdit);
     
        textEdit->setAcceptDrops(false);
        setAcceptDrops(true);
     
        setWindowTitle(tr("Text Editor"));
    }
     
    MainWindow::~MainWindow()
    {
    }

在构造函数中，我们创建了 QTextEdit 的对象。默认情况下，QTextEdit 可以接受从其它应用程序拖放过来的文本类型的数据。如果用户把一个文件拖到这面，默认会把文件名插入到光标位置。但是我们希望让 MainWindow 读取文件内容，而不是仅仅插入文件名，所以我们在 MainWindow 中加入了拖放操作。首先要把 QTextEdit 的 setAcceptDrops() 函数置为 false，并且把 MainWindow 的 setAcceptDrops() 置为 true，这样我们就能够让 MainWindow 截获拖放事件，而不是交给 QTextEdit 处理。

.. code-block:: c++

    void MainWindow::dragEnterEvent(QDragEnterEvent *event)
    {
        if (event->mimeData()->hasFormat("text/uri-list")) {
            event->acceptProposedAction();
        }
    }

当用户将对象拖动到组件上面时，系统会回调 dragEnterEvent() 函数。如果我们在事件处理代码中调用 acceptProposeAction() 函数，就可以向用户暗示，你可以将拖动的对象放在这个组件上。默认情况下，组件是不会接受拖放的。如果我们调用了这个函数，那么 Qt 会自动以光标样式的变化来提示用户是否可以将对象放在组件上。在这里，我们希望告诉用户，窗口可以接受拖放，但是我们仅接受某一种类型的文件，而不是全部文件。我们首先检查拖放文件的 MIME 类型信息。MIME 类型由 Internet Assigned Numbers Authority (IANA) 定义，Qt 的拖放事件使用 MIME 类型来判断拖放对象的类型。关于 MIME 类型的详细信息，请参考 `http://www.iana.org/assignments/media-types/ <http://www.iana.org/assignments/media-types/>`_。MIME 类型为 text/uri-list 通常用来描述一个 URI 列表。这些 URI 可以是文件名，可以是 URL 或者其它的资源描述符。如果发现用户拖放的是一个 text/uri-list 数据（即文件名），我们便接受这个动作。

.. code-block:: c++

    void MainWindow::dropEvent(QDropEvent *event)
    {
        QList urls = event->mimeData()->urls();
        if (urls.isEmpty()) {
            return;
        }
     
        QString fileName = urls.first().toLocalFile();
        if (fileName.isEmpty()) {
            return;
        }
     
        if (readFile(fileName)) {
            setWindowTitle(tr("%1 - %2").arg(fileName, tr("Drag File")));
        }
    }
     
    bool MainWindow::readFile(const QString &fileName)
    {
        bool r = false;
        QFile file(fileName);
        QString content;
        if(file.open(QIODevice::ReadOnly)) {
            content = file.readAll();
            r = true;
        }
        textEdit->setText(content);
        return r;
    }

当用户将对象释放到组件上面时，系统回调 dropEvent() 函数。我们使用 QMimeData::urls() 来获得 QUrl 的一个列表。通常，这种拖动应该只有一个文件，但是也不排除多个文件一起拖动。因此我们需要检查这个列表是否为空，如果不为空，则取出第一个，否则立即返回。最后我们调用 readFile() 函数读取文件内容。这个函数的内容很简单，我们前面也讲解过有关文件的操作，这里不再赘述。现在可以运行下看看效果了。

接下来的例子也是来自 C++ GUI Programming with Qt4, 2nd Edition。在这个例子中，我们将创建左右两个并列的列表，可以实现二者之间数据的相互拖动。

.. code-block:: c++

    class ProjectListWidget : public QListWidget
    {
        Q_OBJECT
    public:
        ProjectListWidget(QWidget *parent = 0);
    protected:
        void mousePressEvent(QMouseEvent *event);
        void mouseMoveEvent(QMouseEvent *event);
        void dragEnterEvent(QDragEnterEvent *event);
        void dragMoveEvent(QDragMoveEvent *event);
        void dropEvent(QDropEvent *event);
    private:
        void performDrag();
        QPoint startPos;
    };

ProjectListWidget 是我们的列表的实现。这个类继承自 QListWidget。在最终的程序中，将会是两个 ProjectListWidget 的并列。

.. code-block:: c++

    ProjectListWidget::ProjectListWidget(QWidget *parent)
        : QListWidget(parent)
    {
        setAcceptDrops(true);
    }

构造函数我们设置了 setAcceptDrops()，使 ProjectListWidget 能够支持拖动操作。

.. code-block:: c++

    void ProjectListWidget::mousePressEvent(QMouseEvent *event)
    {
        if (event->button() == Qt::LeftButton)
            startPos = event->pos();
        QListWidget::mousePressEvent(event);
    }
     
    void ProjectListWidget::mouseMoveEvent(QMouseEvent *event)
    {
        if (event->buttons() & Qt::LeftButton) {
            int distance = (event->pos() - startPos).manhattanLength();
            if (distance >= QApplication::startDragDistance())
                performDrag();
        }
        QListWidget::mouseMoveEvent(event);
    }
     
    void ProjectListWidget::performDrag()
    {
        QListWidgetItem *item = currentItem();
        if (item) {
            QMimeData *mimeData = new QMimeData;
            mimeData->setText(item->text());
     
            QDrag *drag = new QDrag(this);
            drag->setMimeData(mimeData);
            drag->setPixmap(QPixmap(":/images/person.png"));
            if (drag->exec(Qt::MoveAction) == Qt::MoveAction)
                delete item;
        }
    }

mousePressEvent() 函数中，我们检测鼠标左键点击，如果是的话就记录下当前位置。需要注意的是，这个函数最后需要调用系统自带的处理函数，以便实现通常的那种操作。这在一些重写事件的函数中都是需要注意的，前面我们已经反复强调过这一点。

mouseMoveEvent() 函数判断了，如果鼠标在移动的时候一直按住左键（也就是 if 里面的内容），那么就计算一个 manhattanLength() 值。从字面上翻译，这是个“曼哈顿长度”。首先来看看 event.pos() – startPos 是什么。在 mousePressEvent() 函数中，我们将鼠标按下的坐标记录为 startPos，而 event.pos() 则是鼠标当前的坐标：一个点减去另外一个点，这就是一个位移向量。所谓曼哈顿距离就是两点之间的距离（按照勾股定理进行计算而来），也就是这个向量的长度。然后继续判断，如果大于 QApplication::startDragDistance()，我们才进行释放的操作。当然，最后还是要调用系统默认的鼠标拖动函数。这一判断的意义在于，防止用户因为手的抖动等因素造成的鼠标拖动。用户必须将鼠标拖动一段距离之后，我们才认为他是希望进行拖动操作，而这一距离就是 QApplication::startDragDistance() 提供的，这个值通常是 4px。

performDrag() 开始处理拖放的过程。这里，我们要创建一个 QDrag 对象，将 this 作为 parent。QDrag 使用 QMimeData 存储数据。例如我们使用 QMimeData::setText() 函数将一个字符串存储为 text/plain 类型的数据。QMimeData 提供了很多函数，用于存储诸如 URL、颜色等类型的数据。使用 QDrag::setPixmap() 则可以设置拖动发生时鼠标的样式。QDrag::exec() 会阻塞拖动的操作，直到用户完成操作或者取消操作。它接受不同类型的动作作为参数，返回值是真正执行的动作。这些动作的类型一般为 Qt::CopyAction，Qt::MoveAction 和 Qt::LinkAction。返回值会有这几种动作，同时还会有一个 Qt::IgnoreAction 用于表示用户取消了拖放。这些动作取决于拖放源对象允许的类型，目的对象接受的类型以及拖放时按下的键盘按键。在 exec() 调用之后，Qt 会在拖放对象不需要的时候释放掉。

.. code-block:: c++

    void ProjectListWidget::dragMoveEvent(QDragMoveEvent *event)
    {
        ProjectListWidget *source =
                qobject_cast(event->source());
        if (source && source != this) {
            event->setDropAction(Qt::MoveAction);
            event->accept();
        }
    }
     
    void ProjectListWidget::dropEvent(QDropEvent *event)
    {
        ProjectListWidget *source =
                qobject_cast(event->source());
        if (source && source != this) {
            addItem(event->mimeData()->text());
            event->setDropAction(Qt::MoveAction);
            event->accept();
        }
    }

dragMoveEvent() 和 dropEvent() 相似。首先判断事件的来源（source），由于我们是两个 ProjectListWidget 之间相互拖动，所以来源应该是 ProjectListWidget 类型的（当然，这个 source 不能是自己，所以我们还得判断 source != this）。dragMoveEvent() 中我们检查的是被拖动的对象；dropEvent() 中我们检查的是释放的对象：这二者是不同的。

附件：:download:`ProjectListWidget <srcs/ProjectListWidget.zip>`