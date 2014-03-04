.. _dnd_data:

`53. 自定义拖放数据 <http://www.devbean.net/2013/05/qt-study-road-2-dnd-data/>`_
================================================================================

:作者: 豆子

:日期: 2013年05月26日

上一章中，我们的例子使用系统提供的拖放对象 QMimeData 进行拖放数据的存储。比如使用 QMimeData::setText() 创建文本，使用 QMimeData::urls() 创建 URL 对象等。但是，如果你希望使用一些自定义的对象作为拖放数据，比如自定义类等等，单纯使用 QMimeData 可能就没有那么容易了。为了实现这种操作，我们可以从下面三种实现方式中选择一个：

1. 将自定义数据作为 QByteArray 对象，使用 QMimeData::setData() 函数作为二进制数据存储到 QMimeData 中，然后使用 QMimeData::Data() 读取
2. 继承 QMimeData，重写其中的 formats() 和 retrieveData() 函数操作自定义数据
3. 如果拖放操作仅仅发生在同一个应用程序，可以直接继承 QMimeData，然后使用任意合适的数据结构进行存储

这三种选择各有千秋：第一种方法不需要继承任何类，但是有一些局限：即是拖放不会发生，我们也必须将自定义的数据对象转换成 QByteArray 对象，在一定程度上，这会降低程序性能；另外，如果你希望支持很多种拖放的数据，那么每种类型的数据都必须使用一个 QMimeData 类，这可能会导致类爆炸。后两种实现方式则不会有这些问题，或者说是能够减小这种问题，并且能够让我们有完全的控制权。

下面我们使用第一种方法来实现一个表格。这个表格允许我们选择一部分数据，然后拖放到另外的一个空白表格中。在数据拖动过程中，我们使用 CSV 格式对数据进行存储。

首先来看头文件：

.. code-block:: c++

    class DataTableWidget : public QTableWidget
    {
        Q_OBJECT
    public:
        DataTableWidget(QWidget *parent = 0);
    protected:
        void mousePressEvent(QMouseEvent *event);
        void mouseMoveEvent(QMouseEvent *event);
        void dragEnterEvent(QDragEnterEvent *event);
        void dragMoveEvent(QDragMoveEvent *event);
        void dropEvent(QDropEvent *event);
    private:
        void performDrag();
        QString selectionText() const;
     
        QString toHtml(const QString &plainText) const;
        QString toCsv(const QString &plainText) const;
        void fromCsv(const QString &csvText);
     
        QPoint startPos;
    };

这里，我们的表格继承自 QTableWidget。虽然这是一个简化的 QTableView，但对于我们的演示程序已经绰绰有余。

.. code-block:: c++

    DataTableWidget::DataTableWidget(QWidget *parent)
        : QTableWidget(parent)
    {
        setAcceptDrops(true);
        setSelectionMode(ContiguousSelection);
     
        setColumnCount(3);
        setRowCount(5);
    }
     
    void DataTableWidget::mousePressEvent(QMouseEvent *event)
    {
        if (event->button() == Qt::LeftButton) {
            startPos = event->pos();
        }
        QTableWidget::mousePressEvent(event);
    }
     
    void DataTableWidget::mouseMoveEvent(QMouseEvent *event)
    {
        if (event->buttons() & Qt::LeftButton) {
            int distance = (event->pos() - startPos).manhattanLength();
            if (distance >= QApplication::startDragDistance()) {
                performDrag();
            }
        }
    }
     
    void DataTableWidget::dragEnterEvent(QDragEnterEvent *event)
    {
        DataTableWidget *source =
                qobject_cast<DataTableWidget *>(event->source());
        if (source && source != this) {
            event->setDropAction(Qt::MoveAction);
            event->accept();
        }
    }
     
    void DataTableWidget::dragMoveEvent(QDragMoveEvent *event)
    {
        DataTableWidget *source =
                qobject_cast<DataTableWidget *>(event->source());
        if (source && source != this) {
            event->setDropAction(Qt::MoveAction);
            event->accept();
        }
    }

构造函数中，由于我们要针对两个表格进行相互拖拽，所以我们设置了 setAcceptDrops() 函数。选择模式设置为连续，这是为了方便后面我们的算法简单。mousePressEvent()，mouseMoveEvent()，dragEnterEvent() 以及 dragMoveEvent() 四个事件响应函数与前面几乎一摸一样，这里不再赘述。注意，这几个函数中有一些并没有调用父类的同名函数。关于这一点我们在前面的章节中曾反复强调，但这里我们不希望父类的实现被执行，因此完全屏蔽了父类实现。下面我们来看 performDrag() 函数：

.. code-block:: c++

    void DataTableWidget::performDrag()
    {
        QString selectedString = selectionText();
        if (selectedString.isEmpty()) {
            return;
        }
     
        QMimeData *mimeData = new QMimeData;
        mimeData->setHtml(toHtml(selectedString));
        mimeData->setData("text/csv", toCsv(selectedString).toUtf8());
     
        QDrag *drag = new QDrag(this);
        drag->setMimeData(mimeData);
        if (drag->exec(Qt::CopyAction | Qt::MoveAction) == Qt::MoveAction) {
             selectionModel()->clearSelection();
        }
    }

首先我们获取选择的文本（selectionText() 函数），如果为空则直接返回。然后创建一个 QMimeData 对象，设置了两个数据：HTML 格式和 CSV 格式。我们的 CSV 格式是以 QByteArray 形式存储的。之后我们创建了 QDrag 对象，将这个 QMimeData 作为拖动时所需要的数据，执行其 exec() 函数。exec() 函数指明，这里的拖动操作接受两种类型：复制和移动。当执行的是移动时，我们将已选区域清除。

需要注意一点，QMimeData 在创建时并没有提供 parent 属性，这意味着我们必须手动调用 delete 将其释放。但是，setMimeData() 函数会将其所有权转移到 QDrag 名下，也就是会将其 parent 属性设置为这个 QDrag。这意味着，当 QDrag 被释放时，其名下的所有 QMimeData 对象都会被释放，所以结论是，我们实际是无需，也不能手动 delete 这个 QMimeData 对象。

.. code-block:: c++

    void DataTableWidget::dropEvent(QDropEvent *event)
    {
        if (event->mimeData()->hasFormat("text/csv")) {
            QByteArray csvData = event->mimeData()->data("text/csv");
            QString csvText = QString::fromUtf8(csvData);
            fromCsv(csvText);
            event->acceptProposedAction();
        }
    }

dropEvent() 函数也很简单：如果是 CSV 类型，我们取出数据，转换成字符串形式，调用了 fromCsv() 函数生成新的数据项。

几个辅助函数的实现比较简单：

.. code-block:: c++

    QString DataTableWidget::selectionText() const
    {
        QString selectionString;
        QString headerString;
        QAbstractItemModel *itemModel = model();
        QTableWidgetSelectionRange selection = selectedRanges().at(0);
        for (int row = selection.topRow(), firstRow = row;
             row <= selection.bottomRow(); row++) {
            for (int col = selection.leftColumn();
                 col <= selection.rightColumn(); col++) {
                if (row == firstRow) {
                    headerString.append(horizontalHeaderItem(col)->text()).append("\t");
                }
                QModelIndex index = itemModel->index(row, col);
                selectionString.append(index.data().toString()).append("\t");
            }
            selectionString = selectionString.trimmed();
            selectionString.append("\n");
        }
        return headerString.trimmed() + "\n" + selectionString.trimmed();
    }
     
    QString DataTableWidget::toHtml(const QString &plainText) const
    {
    #if QT_VERSION >= 0x050000
        QString result = plainText.toHtmlEscaped();
    #else
        QString result = Qt::escape(plainText);
    #endif
        result.replace("\t", "<td>");
        result.replace("\n", "\n<tr><td>");
        result.prepend("<table>\n<tr><td>");
        result.append("\n</table>");
        return result;
    }
     
    QString DataTableWidget::toCsv(const QString &plainText) const
    {
        QString result = plainText;
        result.replace("\\", "\\\\");
        result.replace("\"", "\\\"");
        result.replace("\t", "\", \"");
        result.replace("\n", "\"\n\"");
        result.prepend("\"");
        result.append("\"");
        return result;
    }
     
    void DataTableWidget::fromCsv(const QString &csvText)
    {
        QStringList rows = csvText.split("\n");
        QStringList headers = rows.at(0).split(", ");
        for (int h = 0; h < headers.size(); ++h) {
            QString header = headers.at(0);
            headers.replace(h, header.replace('"', ""));
        }
        setHorizontalHeaderLabels(headers);
        for (int r = 1; r < rows.size(); ++r) {
            QStringList row = rows.at(r).split(", ");
            setItem(r - 1, 0, new QTableWidgetItem(row.at(0).trimmed().replace('"', "")));
            setItem(r - 1, 1, new QTableWidgetItem(row.at(1).trimmed().replace('"', "")));
        }
    }

虽然看起来很长，但是这几个函数都是纯粹算法，而且算法都比较简单。注意 toHtml() 中我们使用条件编译语句区分了一个 Qt4 与 Qt5 的不同函数。这也是让同一代码能够同时应用于 Qt4 和 Qt5 的技巧。fromCsv() 函数中，我们直接将下面表格的前面几列设置为拖动过来的数据，注意这里有一些格式上面的变化，主要用于更友好地显示。

最后是 MainWindow 的一个简单实现：

.. code-block:: c++

    MainWindow::MainWindow(QWidget *parent) :
        QMainWindow(parent)
    {
        topTable = new DataTableWidget(this);
        QStringList headers;
        headers << "ID" << "Name" << "Age";
        topTable->setHorizontalHeaderLabels(headers);
        topTable->setItem(0, 0, new QTableWidgetItem(QString("0001")));
        topTable->setItem(0, 1, new QTableWidgetItem(QString("Anna")));
        topTable->setItem(0, 2, new QTableWidgetItem(QString("20")));
        topTable->setItem(1, 0, new QTableWidgetItem(QString("0002")));
        topTable->setItem(1, 1, new QTableWidgetItem(QString("Tommy")));
        topTable->setItem(1, 2, new QTableWidgetItem(QString("21")));
        topTable->setItem(2, 0, new QTableWidgetItem(QString("0003")));
        topTable->setItem(2, 1, new QTableWidgetItem(QString("Jim")));
        topTable->setItem(2, 2, new QTableWidgetItem(QString("21")));
        topTable->setItem(3, 0, new QTableWidgetItem(QString("0004")));
        topTable->setItem(3, 1, new QTableWidgetItem(QString("Dick")));
        topTable->setItem(3, 2, new QTableWidgetItem(QString("24")));
        topTable->setItem(4, 0, new QTableWidgetItem(QString("0005")));
        topTable->setItem(4, 1, new QTableWidgetItem(QString("Tim")));
        topTable->setItem(4, 2, new QTableWidgetItem(QString("22")));
     
        bottomTable = new DataTableWidget(this);
     
        QWidget *content = new QWidget(this);
        QVBoxLayout *layout = new QVBoxLayout(content);
        layout->addWidget(topTable);
        layout->addWidget(bottomTable);
     
        setCentralWidget(content);
     
        setWindowTitle("Data Table");
    }

这段代码没有什么新鲜内容，我们直接将其跳过。最后编译运行下程序，按下 shift 并点击表格两个单元格即可选中，然后拖放到另外的空白表格中来查看效果。

下面我们换用继承 QMimeData 的方法来尝试重新实现上面的功能。

.. code-block:: c++

    class TableMimeData : public QMimeData
    {
        Q_OBJECT
    public:
        TableMimeData(const QTableWidget *tableWidget,
                      const QTableWidgetSelectionRange &range);
        const QTableWidget *tableWidget() const
        {
            return dataTableWidget;
        }
        QTableWidgetSelectionRange range() const
        {
            return selectionRange;
        }
        QStringList formats() const
        {
            return dataFormats;
        }
    protected:
        QVariant retrieveData(const QString &format,
                              QVariant::Type preferredType) const;
    private:
        static QString toHtml(const QString &plainText);
        static QString toCsv(const QString &plainText);
        QString text(int row, int column) const;
        QString selectionText() const;
     
        const QTableWidget *dataTableWidget;
        QTableWidgetSelectionRange selectionRange;
        QStringList dataFormats;
    };

为了避免存储具体的数据，我们存储表格的指针和选择区域的坐标的指针；dataFormats 指明这个数据对象所支持的数据格式。这个格式列表由 formats() 函数返回，意味着所有被 MIME 数据对象支持的数据类型。这个列表是没有先后顺序的，但是最佳实践是将“最适合”的类型放在第一位。对于支持多种类型的应用程序而言，有时候会直接选用第一个符合的类型存储。

.. code-block:: c++

    TableMimeData::TableMimeData(const QTableWidget *tableWidget,
                                 const QTableWidgetSelectionRange &range)
    {
        dataTableWidget = tableWidget;
        selectionRange = range;
        dataFormats << "text/csv" << "text/html";
    }

函数 retrieveData() 将给定的 MIME 类型作为 QVariant 返回。参数 format 的值通常是 formats() 函数返回值之一，但是我们并不能假定一定是这个值之一，因为并不是所有的应用程序都会通过 formats() 函数检查 MIME 类型。一些返回函数，比如 text()，html()，urls()，imageData()，colorData() 和 data() 实际上都是在 QMimeData 的 retrieveData() 函数中实现的。第二个参数 preferredType 给出我们应该在 QVariant 中存储哪种类型的数据。在这里，我们简单的将其忽略了，并且在 else 语句中，我们假定 QMimeData 会自动将其转换成所需要的类型：

.. code-block:: c++

    QVariant TableMimeData::retrieveData(const QString &format,
                                         QVariant::Type preferredType) const
    {
        if (format == "text/csv") {
            return toCsv(selectionText());
        } else if (format == "text/html") {
            return toHtml(selectionText());
        } else {
            return QMimeData::retrieveData(format, preferredType);
        }
    }

在组件的 dragEvent() 函数中，需要按照自己定义的数据类型进行选择。我们使用 qobject_cast 宏进行类型转换。如果成功，说明数据来自同一应用程序，因此我们直接设置 QTableWidget 相关数据，如果转换失败，我们则使用一般的处理方式。这也是这类程序通常的处理方式：

.. code-block:: c++

    void DataTableWidget::dropEvent(QDropEvent *event)
    {
        const TableMimeData *tableData =
                qobject_cast<const TableMimeData *>(event->mimeData());
     
        if (tableData) {
            const QTableWidget *otherTable = tableData->tableWidget();
            QTableWidgetSelectionRange otherRange = tableData->range();
            // ...
            event->acceptProposedAction();
        } else if (event->mimeData()->hasFormat("text/csv")) {
            QByteArray csvData = event->mimeData()->data("text/csv");
            QString csvText = QString::fromUtf8(csvData);
            // ...
            event->acceptProposedAction();
        }
        QTableWidget::mouseMoveEvent(event);
    }

由于这部分代码与前面的相似，感兴趣的童鞋可以根据前面的代码补全这部分，所以这里不再给出完整代码。
