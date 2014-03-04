.. _show_sql_data:

`57. 可视化显示数据库数据 <http://www.devbean.net/2013/06/qt-study-road-2-show-sql-data/>`_
===========================================================================================

:作者: 豆子

:日期: 2013年06月26日

前面我们用了两个章节介绍了 Qt 提供的两种操作数据库的方法。显然，使用 QSqlQuery 的方式更灵活，功能更强大，而使用 QSqlTableModel 则更简单，更方便与 model/view 结合使用（数据库应用很大一部分就是以表格形式显示出来，这正是 model/view 的强项）。本章我们简单介绍使用 QSqlTableModel 显示数据的方法。当然，我们也可以选择使用 QSqlQuery 获取数据，然后交给 view 显示，而这需要自己给 model 提供数据。鉴于我们前面已经详细介绍过如何使用自定义 model 以及如何使用 QTableWidget，所以我们这里不再详细说明这一方法。


我们还是使用前面一直在用的 student 表，直接来看代码：

.. code-block:: c++

    int main(int argc, char *argv[])
    {
        QApplication a(argc, argv);
        if (connect("demo.db")) {
            QSqlTableModel *model = new QSqlTableModel;
            model->setTable("student");
            model->setSort(1, Qt::AscendingOrder);
            model->setHeaderData(1, Qt::Horizontal, "Name");
            model->setHeaderData(2, Qt::Horizontal, "Age");
            model->select();
     
            QTableView *view = new QTableView;
            view->setModel(model);
            view->setSelectionMode(QAbstractItemView::SingleSelection);
            view->setSelectionBehavior(QAbstractItemView::SelectRows);
    //        view->setColumnHidden(0, true);
            view->resizeColumnsToContents();
            view->setEditTriggers(QAbstractItemView::NoEditTriggers);
     
            QHeaderView *header = view->horizontalHeader();
            header->setStretchLastSection(true);
     
            view->show();
        } else {
            return 1;
        }
        return a.exec();
    }

这里的 connect() 函数还是我们前面使用过的，我们主要关注剩下的代码。

正如前一章的代码所示，我们在 main() 函数中创建了 QSqlTableModel 对象，使用 student 表。student 表有三列：id，name 和 age，我们选择按照 name 排序，使用 setSort() 函数达到这一目的。然后我们设置每一列的列头。这里我们只使用了后两列，第一列没有设置，所以依旧显示为列名 id。

在设置好 model 之后，我们又创建了 QTableView 对象作为视图。注意这里的设置：单行选择，按行选择。resizeColumnsToContents() 说明每列宽度适配其内容；setEditTriggers() 则禁用编辑功能。最后，我们设置最后一列要充满整个窗口。我们的代码中有一行注释，设置第一列不显示。由于我们使用了 QSqlTableModel 方式，不能按列查看，所以我们在视图级别上面做文章：将不想显示的列隐藏掉。

接下来运行代码即可看到效果：

.. admonition:: 数据库显示

    .. image:: imgs/57/sql-model-view.png

如果看到代码中很多“魔术数字”，更好的方法是，使用一个枚举将这些魔术数字隐藏掉，这也是一种推荐的方式：

.. code-block:: c++

    enum ColumnIndex
    {
        Column_ID = 0,
        Column_Name = 1,
        Column_Age = 2
    };
     
    int main(int argc, char *argv[])
    {
        QApplication a(argc, argv);
        if (connect("demo.db")) {
            QSqlTableModel *model = new QSqlTableModel;
            model->setTable("student");
            model->setSort(Column_Name, Qt::AscendingOrder);
            model->setHeaderData(Column_Name, Qt::Horizontal, "Name");
            model->setHeaderData(Column_Age, Qt::Horizontal, "Age");
            model->select();
     
            QTableView *view = new QTableView;
            view->setModel(model);
            view->setSelectionMode(QAbstractItemView::SingleSelection);
            view->setSelectionBehavior(QAbstractItemView::SelectRows);
            view->setColumnHidden(Column_ID, true);
            view->resizeColumnsToContents();
            view->setEditTriggers(QAbstractItemView::NoEditTriggers);
     
            QHeaderView *header = view->horizontalHeader();
            header->setStretchLastSection(true);
     
            view->show();
        } else {
            return 1;
        }
        return a.exec();
    }
