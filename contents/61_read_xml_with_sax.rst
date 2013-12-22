.. _read_xml_with_sax:

`61. 使用 SAX 处理 XML <http://www.devbean.net/2013/08/qt-study-road-2-read-xml-with-sax/>`_
============================================================================================

:作者: 豆子

:日期: 2013年08月13日

前面两章我们介绍了使用流和 DOM 的方式处理 XML 的相关内容，本章将介绍处理 XML 的最后一种方式：SAX。SAX 是一种读取 XML 文档的标准 API，同 DOM 类似，并不以语言为区别。Qt 的 SAX 类基于 SAX2 的 Java 实现，不过具有一些必要的名称上的转换。相比 DOM，SAX 的实现更底层因而处理起来通常更快。但是，我们前面介绍的 QXmlStreamReader 类更偏向 Qt 风格的 API，并且比 SAX 处理器更快，所以，现在我们之所以使用 SAX API，更主要的是为了把 SAX API 引入 Qt。在我们通常的项目中，并不需要真的使用 SAX。

Qt 提供了 QXmlSimpleReader 类，提供基于 SAX 的 XML 处理。同前面所说的 DOM 方式类似，这个类也不会对 XML 文档进行有效性验证。QXmlSimpleReader 可以识别良格式的 XML 文档，支持 XML 命名空间。当这个处理器读取 XML 文档时，每当到达一个特定位置，都会调用一个用于处理解析事件的处理类。注意，这里所说的“事件”，不同于 Qt 提供的鼠标键盘事件，这仅是处理器在到达预定位置时发出的一种通知。例如，当处理器遇到一个标签的开始时，会发出“新开始一个标签”这个通知，也就是一个事件。我们可以从下面的例子中来理解这一点：

.. code-block:: none

    <doc>
        <quote>Gnothi seauton</quote>
    </doc>

当读取这个 XML 文档时，处理器会依次发出下面的事件：

.. code-block:: c++

    startDocument()
    startElement("doc")
    startElement("quote")
    characters("Gnothi seauton")
    endElement("quote")
    endElement("doc")
    endDocument()

每出现一个事件，都会有一个回调，这个回调函数就是在称为 Handler 的处理类中定义的。上面给出的事件都是在 QXmlContentHandler 接口中定义的。为简单起见，我们省略了一些函数。QXmlContentHandler 仅仅是众多处理接口中的一个，我们还有 QXmlEntityResolver，QXmlDTDHandler，QXmlErrorHandler，QXmlDeclHandler 以及 QXmlLexicalHandler 等。这些接口都是纯虚类，分别定义了不同类型的处理事件。对于大多数应用程序，QXmlContentHandler 和 QXmlErrorHandler 是最常用的两个。

为简化处理，Qt 提供了一个 QXmlDefaultHandler。这个类实现了以上所有的接口，每个函数都提供了一个空白实现。也就是说，当我们需要实现一个处理器时，只需要继承这个类，覆盖我们所关心的几个函数即可，无需将所有接口定义的函数都实现一遍。这种设计在 Qt 中并不常见，但是如果你熟悉 Java，就会感觉非常亲切。Java 中很多接口都是如此设计的。

使用 SAX API 与 QXmlStreamReader 或者 DOM API 之间最大的区别是，使用 SAX API 要求我们必须自己记录当前解析的状态。在另外两种实现中，这并不是必须的，我们可以使用递归轻松地处理，但是 SAX API 则不允许（回忆下，SAX 仅允许一遍读取文档，递归意味着你可以先深入到底部再回来）。

下面我们使用 SAX 的方式重新解析前面两章所出现的示例程序。

.. code-block:: c++

    class MainWindow : public QMainWindow, public QXmlDefaultHandler
    {
        Q_OBJECT
    public:
        MainWindow(QWidget *parent = 0);
        ~MainWindow();

        bool readFile(const QString &fileName);

    protected:
        bool startElement(const QString &namespaceURI,
                          const QString &localName,
                          const QString &qName,
                          const QXmlAttributes &attributes);
        bool endElement(const QString &namespaceURI,
                        const QString &localName,
                        const QString &qName);
        bool characters(const QString &str);
        bool fatalError(const QXmlParseException &exception);
    private:
        QTreeWidget *treeWidget;
        QTreeWidgetItem *currentItem;
        QString currentText;
    };

注意，我们的 MainWindow 不仅继承了 QMainWindow，还继承了 QXmlDefaultHandler。也就是说，主窗口自己就是 XML 的解析器。我们重写了 startElement()，endElement()，characters()，fatalError() 几个函数，其余函数不关心，所以使用了父类的默认实现。成员变量相比前面的例子也多出两个，为了记录当前解析的状态。

MainWindow 的构造函数和析构函数同前面没有变化：

.. code-block:: c++

    MainWindow::MainWindow(QWidget *parent)
        : QMainWindow(parent)
    {
        setWindowTitle(tr("XML Reader"));

        treeWidget = new QTreeWidget(this);
        QStringList headers;
        headers << "Items" << "Pages";
        treeWidget->setHeaderLabels(headers);
        setCentralWidget(treeWidget);
    }

    MainWindow::~MainWindow()
    {
    }

下面来看 readFile() 函数：

.. code-block:: c++

    bool MainWindow::readFile(const QString &fileName)
    {
        currentItem = 0;

        QFile file(fileName);
        QXmlInputSource inputSource(&file);
        QXmlSimpleReader reader;
        reader.setContentHandler(this);
        reader.setErrorHandler(this);
        return reader.parse(inputSource);
    }

这个函数中，首先将成员变量清空，然后读取 XML 文档。注意我们使用了 QXmlSimpleReader，将 ContentHandler 和 ErrorHandler 设置为自身。因为我们仅重写了 ContentHandler 和 ErrorHandler 的函数。如果我们还需要另外的处理，还需要继续设置其它的 handler。parse() 函数是 QXmlSimpleReader 提供的函数，开始进行 XML 解析。

.. code-block:: c++

    bool MainWindow::startElement(const QString & /*namespaceURI*/,
                                  const QString & /*localName*/,
                                  const QString &qName,
                                  const QXmlAttributes &attributes)
    {
        if (qName == "entry") {
            currentItem = new QTreeWidgetItem(currentItem ?
                    currentItem : treeWidget->invisibleRootItem());
            currentItem->setText(0, attributes.value("term"));
        } else if (qName == "page") {
            currentText.clear();
        }
        return true;
    }

startElement() 在读取到一个新的开始标签时被调用。这个函数有四个参数，我们这里主要关心第三和第四个参数：第三个参数是标签的名字（正式的名字是“限定名”，qualified name，因此形参是 qName）；第四个参数是属性列表。前两个参数主要用于带有命名空间的 XML 文档的处理，现在我们不关心命名空间。函数开始，如果是 <entry> 标签，我们创建一个新的 QTreeWidgetItem。如果这个标签是嵌套在另外的 <entry> 标签中的，currentItem 被定义为当前标签的子标签，否则则是根标签。我们使用 setText() 函数设置第一列的值，同前面的章节类似。如果是 <page> 标签，我们将 currentText 清空，准备接下来的处理。最后，我们返回 true，告诉 SAX 继续处理文件。如果有任何错误，则可以返回 false 告诉 SAX 停止处理。此时，我们需要覆盖 QXmlDefaultHandler 的 errorString() 函数来返回一个恰当的错误信息。

.. code-block:: c++

    bool MainWindow::characters(const QString &str)
    {
        currentText += str;
        return true;
    }

注意下我们的 XML 文档。characters() 仅在 <page> 标签中出现。因此我们在 characters() 中直接追加 currentText。

.. code-block:: c++

    bool MainWindow::endElement(const QString & /*namespaceURI*/,
                                const QString & /*localName*/,
                                const QString &qName)
    {
        if (qName == "entry") {
            currentItem = currentItem->parent();
        } else if (qName == "page") {
            if (currentItem) {
                QString allPages = currentItem->text(1);
                if (!allPages.isEmpty())
                    allPages += ", ";
                allPages += currentText;
                currentItem->setText(1, allPages);
            }
        }
        return true;
    }

endElement() 在遇到结束标签时调用。和 startElement() 类似，这个函数的第三个参数也是标签的名字。我们检查如果是 </entry>，则将 currentItem 指向其父节点。这保证了 currentItem 恢复到处理 <entry> 标签之前所指向的节点。如果是 </page>，我们需要把新读到的 currentText 追加到第二列。

.. code-block:: c++

    bool MainWindow::fatalError(const QXmlParseException &exception)
    {
        QMessageBox::critical(this,
                              tr("SAX Error"),
                              tr("Parse error at line %1, column %2:\n %3")
                              .arg(exception.lineNumber())
                              .arg(exception.columnNumber())
                              .arg(exception.message()));
        return false;
    }

当遇到处理失败的时候，SAX 会回调 fatalError() 函数。我们这里仅仅向用户显示出来哪里遇到了错误。如果你想看这个函数的运行，可以将 XML 文档修改为不合法的形式。

我们程序的运行结果同前面还是一样的，这里也不再赘述了。
