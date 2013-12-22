.. _save_xml:

`62. 保存 XML <http://www.devbean.net/2013/08/qt-study-road-2-save-xml/>`_
==========================================================================

:作者: 豆子

:日期: 2013年08月26日

前面几章我们讨论了读取 XML 文档的三种方法。虽然各有千秋，但是 Qt 推荐的是使用 QXmlStreamReader。与此同时，许多应用程序不仅需要读取 XML，还需要写入 XML。为此，Qt 同样提供了三种方法：

1. 使用 QXmlStreamWriter；
2. 构造一个 DOM 树，然后掉其 save() 函数；
3. 使用 QString 手动生成 XML。

可以看出，无论我们使用哪种读取方式，这几种写入的方法都与此无关。这是因为 W3C 仅仅定义了如何处理 XML 文档，并没有给出如何生成 XML 文档的标准方法（尽管当我们使用 DOM 方式读取的时候，依旧可以使用同样的 DOM 树写入）。

如同 Qt 所推荐的，我们也推荐使用 QXmlStreamWriter 生成 XML 文档。这个类帮助我们做了很多工作，比如特殊字符的转义。接下来我们使用 QXmlStreamWriter 将前面几章使用的 XML 文档生成出来：

.. code-block:: c++

    QFile file("bookindex.xml");
    if (!file.open(QFile::WriteOnly | QFile::Text)) {
        qDebug() << "Error: Cannot write file: "
                 << qPrintable(file.errorString());
        return false;
    }

    QXmlStreamWriter xmlWriter(&file);
    xmlWriter.setAutoFormatting(true);
    xmlWriter.writeStartDocument();
    xmlWriter.writeStartElement("bookindex");
    xmlWriter.writeStartElement("entry");
    xmlWriter.writeAttribute("term", "sidebearings");
    xmlWriter.writeTextElement("page", "10");
    xmlWriter.writeTextElement("page", "34-35");
    xmlWriter.writeTextElement("page", "307-308");
    xmlWriter.writeEndElement();
    xmlWriter.writeStartElement("entry");
    xmlWriter.writeAttribute("term", "subtraction");
    xmlWriter.writeStartElement("entry");
    xmlWriter.writeAttribute("term", "of pictures");
    xmlWriter.writeTextElement("page", "115");
    xmlWriter.writeTextElement("page", "224");
    xmlWriter.writeEndElement();
    xmlWriter.writeStartElement("entry");
    xmlWriter.writeAttribute("term", "of vectors");
    xmlWriter.writeTextElement("page", "9");
    xmlWriter.writeEndElement();
    xmlWriter.writeEndElement();
    xmlWriter.writeEndDocument();
    file.close();
    if (file.error()) {
        qDebug() << "Error: Cannot write file: "
                 << qPrintable(file.errorString());
        return false;
    }
    // ...

首先，我们以只写方式创建一个文件。然后基于该文件我们创建了 QXmlStreamWriter 对象。setAutoFormatting() 函数告诉 QXmlStreamWriter 要有格式输出，也就是会有标签的缩进。我们也可以使用 QXmlStreamWriter::setAutoFormattingIndent() 设置每个缩进所需要的空格数。接下来是一系列以 write 开始的函数。这些函数就是真正输出时需要用到的。注意这些函数以 write 开始，有 Start 和 End 两个对应的名字。正如其名字暗示那样，一个用于写入开始标签，一个用于写入结束标签。writeStartDocument() 开始进行 XML 文档的输出。这个函数会写下

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>

一行。与 writeStartDocument() 相对应的是最后的 writeEndDocument()，告诉 QXmlStreamWriter，这个 XML 文档已经写完。下面我们拿出一段典型的代码：

.. code-block:: c++

    xmlWriter.writeStartElement("entry");
    xmlWriter.writeAttribute("term", "of vectors");
    xmlWriter.writeTextElement("page", "9");
    xmlWriter.writeEndElement();

显然，这里我们首先写下一个 entry 的开始标签，然后给这个标签一个属性 term，属性值是 of vectors。writeTextElement() 函数则会输出一个仅包含文本内容的标签。最后写入这个标签的关闭标签。这段代码的输出结果就是：

.. code-block:: xml

    <entry term="of vectors">
        <page>9</page>
    </entry>

其余部分与此类似，这里不再赘述。这样，我们就输出了一个与前面章节所使用的相同的 XML 文档：

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <bookindex>
        <entry term="sidebearings">
            <page>10</page>
            <page>34-35</page>
            <page>307-308</page>
        </entry>
        <entry term="subtraction">
            <entry term="of pictures">
                <page>115
                <page>224
            </entry>
            <entry term="of vectors">
                <page>9</page>
            </entry>
        </entry>
    </bookindex>

尽管我们推荐使用 QXmlStreamWriter 生成 XML 文档，但是如果现在已经有了 DOM 树，显然直接调用 QDomDocument::save() 函数更为方便。在某些情况下，我们需要手动生成 XML 文档，比如通过 QTextStream：

.. code-block:: c++

    //!!! Qt4
    QTextStream out(&file);
    out.setCodec("UTF-8");
    out << "<doc>\n"
        << "   <quote>" << Qt::escape(quoteText) << "</quote>\n"
        << "   <translation>" << Qt::escape(translationText)
        << "</translation>\n"
        << "</doc>\n";

    //!!! Qt5
    QTextStream out(&file);
    out.setCodec("UTF-8");
    out << "<doc>\n"
        << "   <quote>" << quoteText.toHtmlEscaped() << "</quote>\n"
        << "   <translation>" << translationText.toHtmlEscaped()
        << "</translation>\n"
        << "</doc>\n";

这种办法是最原始的办法：我们直接除了字符串，把字符串拼接成 XML 文档。需要注意的是，quoteText 和 translationText 都需要转义，这是 XML 规范里面要求的，需要将文本中的 <，> 以及 & 进行转义。不过，转义函数在 Qt4 中是 Qt::escape()，而 Qt5 中则是 QString::toHtmlEscaped()，需要按需使用。
