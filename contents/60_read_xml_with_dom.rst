.. _read_xml_with_dom:

`60. 使用 DOM 处理 XML <http://www.devbean.net/2013/08/qt-study-road-2-read-xml-with-dom/>`_
============================================================================================

:作者: 豆子

:日期: 2013年08月03日

DOM 是由 W3C 提出的一种处理 XML 文档的标准接口。Qt 实现了 DOM Level 2 级别的不验证读写 XML 文档的方法。

与上一章所说的流的方式不同，DOM 一次性读入整个 XML 文档，在内存中构造为一棵树（被称为 DOM 树）。我们能够在这棵树上进行导航，比如移动到下一节点或者返回上一节点，也可以对这棵树进行修改，或者是直接将这颗树保存为硬盘上的一个 XML 文件。考虑下面一个 XML 片段：

.. code-block:: xml

    <doc>
        <quote>Scio me nihil scire</quote>
        <translation>I know that I know nothing</translation>
    </doc>

我们可以认为是如下一棵 DOM 树：

.. code-block:: none

    Document
      |--Element(doc)
           |--Element(quote)
           |    |--Text("Scio me nihil scire")
           |--Element(translation)
                |--Text("I know that I know nothing")

上面所示的 DOM 树包含了不同类型的节点。例如，Element 类型的节点有一个开始标签和对应的一个结束标签。在开始标签和结束标签之间的内容作为这个 Element 节点的子节点。在 Qt 中，所有 DOM 节点的类型名字都以 QDom 开头，因此，QDomElement 就是 Element 节点，QDomText 就是 Text 节点。不同类型的节点则有不同类型的子节点。例如，Element 节点允许包含其它 Element 节点，也可以是其它类型，比如 EntityReference，Text，CDATASection，ProcessingInstruction 和 Comment。按照 W3C 的规定，我们有如下的包含规则：

.. code-block:: none

    [Document]
      <- [Element]
      <- DocumentType
      <- ProcessingInstrument
      <- Comment
    [Attr]
      <- [EntityReference]
      <- Text
    [DocumentFragment] | [Element] | [EntityReference] | [Entity]
      <- [Element]
      <- [EntityReference]
      <- Text
      <- CDATASection
      <- ProcessingInstrument
      <- Comment

上面表格中，带有 [] 的可以带有子节点，反之则不能。

下面我们还是以上一章所列出的 books.xml 这个文件来作示例。程序的目的还是一样的：用 QTreeWidget 来显示这个文件的结构。需要注意的是，由于我们选用 DOM 方式处理 XML，无论是 Qt4 还是 Qt5 都需要在 .pro 文件中添加这么一句：

.. code-block:: none

    QT += xml

头文件也是类似的：

.. code-block:: c++

    class MainWindow : public QMainWindow
    {
        Q_OBJECT
    public:
        MainWindow(QWidget *parent = 0);
        ~MainWindow();
     
        bool readFile(const QString &fileName);
    private:
        void parseBookindexElement(const QDomElement &element);
        void parseEntryElement(const QDomElement &element, QTreeWidgetItem *parent);
        void parsePageElement(const QDomElement &element, QTreeWidgetItem *parent);
        QTreeWidget *treeWidget;
    };

MainWindow 的构造函数和析构函数和上一章是一样的，没有任何区别：

.. code-block:: c++

    MainWindow::MainWindow(QWidget *parent)
        : QMainWindow(parent)
    {
        setWindowTitle(tr("XML DOM Reader"));
     
        treeWidget = new QTreeWidget(this);
        QStringList headers;
        headers << "Items" << "Pages";     treeWidget->setHeaderLabels(headers);
        setCentralWidget(treeWidget);
    }
     
    MainWindow::~MainWindow()
    {
    }

readFile() 函数则有了变化：

.. code-block:: c++

    bool MainWindow::readFile(const QString &fileName)
    {
        QFile file(fileName);
        if (!file.open(QFile::ReadOnly | QFile::Text)) {
            QMessageBox::critical(this, tr("Error"),
                                  tr("Cannot read file %1").arg(fileName));
            return false;
        }
     
        QString errorStr;
        int errorLine;
        int errorColumn;
     
        QDomDocument doc;
        if (!doc.setContent(&file, false, &errorStr, &errorLine,
                            &errorColumn)) {
            QMessageBox::critical(this, tr("Error"),
                                  tr("Parse error at line %1, column %2: %3")
                                    .arg(errorLine).arg(errorColumn).arg(errorStr));
            return false;
        }
     
        QDomElement root = doc.documentElement();
        if (root.tagName() != "bookindex") {
            QMessageBox::critical(this, tr("Error"),
                                  tr("Not a bookindex file"));
            return false;
        }
     
        parseBookindexElement(root);
        return true;
    }

readFile() 函数显然更长更复杂。首先需要使用 QFile 打开一个文件，这点没有区别。然后我们创建一个 QDomDocument 对象，代表整个文档。注意看我们上面介绍的结构图，Document 是 DOM 树的根节点，也就是这里的 QDomDocument；使用其 setContent() 函数填充 DOM 树。setContent() 有八个重载，我们使用了其中一个：

.. code-block:: c++

    bool QDomDocument::setContent ( QIODevice * dev,
                                    bool namespaceProcessing,
                                    QString * errorMsg = 0,
                                    int * errorLine = 0,
                                    int * errorColumn = 0 )

不过，这几个重载形式都是调用了同一个实现：

.. code-block:: c++

    bool QDomDocument::setContent ( const QByteArray & data,
                                    bool namespaceProcessing,
                                    QString * errorMsg = 0,
                                    int * errorLine = 0,
                                    int * errorColumn = 0 )

两个函数的参数基本类似。第二个函数有五个参数，第一个是 QByteArray，也就是所读取的真实数据，由 QIODevice 即可获得这个数据，而 QFile 就是 QIODevice 的子类；第二个参数确定是否处理命名空间，如果设置为 true，处理器会自动设置标签的前缀之类，因为我们的 XML 文档没有命名空间，所以直接设置为 false；剩下的三个参数都是关于错误处理。后三个参数都是输出参数，我们传入一个指针，函数会设置指针的实际值，以便我们在外面获取并进行进一步处理。

当 QDomDocument::setContent() 函数调用完毕并且没有错误后，我们调用 QDomDocument::documentElement() 函数获得一个 Document 元素。如果这个 Document 元素标签是 bookindex，则继续向下处理，否则则报错。

.. code-block:: c++

    void MainWindow::parseBookindexElement(const QDomElement &element)
    {
        QDomNode child = element.firstChild();
        while (!child.isNull()) {
            if (child.toElement().tagName() == "entry") {
                parseEntryElement(child.toElement(),
                                  treeWidget->invisibleRootItem());
            }
            child = child.nextSibling();
        }
    }

如果根标签正确，我们取第一个子标签，判断子标签不为空，也就是存在子标签，然后再判断其名字是不是 entry。如果是，说明我们正在处理 entry 标签，则调用其自己的处理函数；否则则取下一个标签（也就是 nextSibling() 的返回值）继续判断。注意我们使用这个 if 只选择 entry 标签进行处理，其它标签直接忽略掉。另外，firstChild() 和 nextSibling() 两个函数的返回值都是 QDomNode。这是所有节点类的基类。当我们需要对节点进行操作时，我们必须将其转换成正确的子类。这个例子中我们使用 toElement() 函数将 QDomNode 转换成 QDomElement。如果转换失败，返回值将是空的 QDomElement 类型，其 tagName() 返回空字符串，if 判断失败，其实也是符合我们的要求的。

.. code-block:: c++

    void MainWindow::parseEntryElement(const QDomElement &element,
                                       QTreeWidgetItem *parent)
    {
        QTreeWidgetItem *item = new QTreeWidgetItem(parent);
        item->setText(0, element.attribute("term"));
     
        QDomNode child = element.firstChild();
        while (!child.isNull()) {
            if (child.toElement().tagName() == "entry") {
                parseEntryElement(child.toElement(), item);
            } else if (child.toElement().tagName() == "page") {
                parsePageElement(child.toElement(), item);
            }
            child = child.nextSibling();
        }
    }

在 parseEntryElement() 函数中，我们创建了一个树组件的节点，其父节点是根节点或另外一个 entry 节点。接着我们又开始遍历这个 entry 标签的子标签。如果是 entry 标签，则递归调用自身，并且把当前节点作为父节点；否则则调用 parsePageElement() 函数。

.. code-block:: c++

    void MainWindow::parsePageElement(const QDomElement &element,
                                      QTreeWidgetItem *parent)
    {
        QString page = element.text();
        QString allPages = parent->text(1);
        if (!allPages.isEmpty()) {
             allPages += ", ";
        }
        allPages += page;
        parent->setText(1, allPages);
    }

parsePageElement() 则比较简单，我们还是通过字符串拼接设置叶子节点的文本。这与上一章的步骤大致相同。

程序运行结果同上一章一模一样，这里不再贴出截图。

通过这个例子我们可以看到，使用 DOM 当时处理 XML 文档，除了一开始的 setContent() 函数，其余部分已经与原始文档没有关系了，也就是说，setContent() 函数的调用之后，已经在内存中构建好了一个完整的 DOM 树，我们可以在这棵树上面进行移动，比如取相邻节点（nextSibling()）。对比上一章流的方式，虽然我们早早关闭文件，但是我们始终使用的是 readNext() 向下移动，同时也不存在 readPrevious() 这样的函数。
