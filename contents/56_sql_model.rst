.. _sql_model:

`56. 使用模型操作数据库 <http://www.devbean.net/2013/06/qt-study-road-2-sql-model/>`_
=====================================================================================

:作者: 豆子

:日期: 2013年06月20日

前一章我们使用 SQL 语句完成了对数据库的常规操作，包括简单的 CREATE、SELECT 等语句的使用。我们也提到过，Qt 不仅提供了这种使用 SQL 语句的方式，还提供了一种基于模型的更高级的处理方式。这种基于 QSqlTableModel 的模型处理更为高级，如果对 SQL 语句不熟悉，并且不需要很多复杂的查询，这种 QSqlTableModel 模型基本可以满足一般的需求。本章我们将介绍 QSqlTableModel 的一般使用，对比 SQL 语句完成对数据库的增删改查等的操作。值得注意的是，QSqlTableModel 并不一定非得结合 QListView 或 QTableView 使用，我们完全可以用其作一般性处理。

首先我们来看看如何使用 QSqlTableModel 进行 SELECT 操作：

.. code-block:: c++

    if (connect("demo.db")) {
        QSqlTableModel model;
        model.setTable("student");
        model.setFilter("age > 20 and age < 25");
        if (model.select()) {
            for (int i = 0; i < model.rowCount(); ++i) {
                QSqlRecord record = model.record(i);
                QString name = record.value("name").toString();
                int age = record.value("age").toInt();
                qDebug() << name << ": " << age;
            }
        }
    } else {
        return 1;
    }

我们依旧使用了前一章的 connect() 函数。接下来我们创建了 QSqlTableModel 实例，使用 setTable() 函数设置所需要操作的表格；setFilter() 函数则是添加过滤器，也就是 WHERE 语句所需要的部分。例如上面代码中的操作实际相当于 SQL 语句

.. code-block:: c++

    SELECT * FROM student WHERE age > 20 AND age < 25

使用 QSqlTableModel::select() 函数进行操作，也就是执行了查询操作。如果查询成功，函数返回 true，由此判断是否发生了错误。如果没有错误，我们使用 record() 函数取出一行记录，该记录是以 QSqlRecord 的形式给出的，而 QSqlRecord::value() 则取出一个列的实际数据值。注意，由于 QSqlTableModel 没有提供 const_iterator 遍历器，因此不能使用 foreach 宏进行遍历。

另外需要注意，由于 QSqlTableModel 只是一种高级操作，肯定没有实际 SQL 语句方便。具体来说，我们使用 QSqlTableModel 只能进行 SELECT * 的查询，不能只查询其中某些列的数据。

下面一段代码则显示了如何使用 QSqlTableModel 进行插入操作：

.. code-block:: c++

    QSqlTableModel model;
    model.setTable("student");
    int row = 0;
    model.insertRows(row, 1);
    model.setData(model.index(row, 1), "Cheng");
    model.setData(model.index(row, 2), 24);
    model.submitAll();

插入也很简单：model.insertRows(row, 1); 说明我们想在索引 0 的位置插入 1 行新的数据。使用 setData() 函数则开始准备实际需要插入的数据。注意这里我们向 row 的第一个位置写入 Cheng（通过 model.index(row, 1)，回忆一下，我们把 model 当作一个二维表，这个坐标相当于第 row 行第 1 列），其余以此类推。最后，调用 submitAll() 函数提交所有修改。这里执行的操作可以用如下 SQL 表示：

.. code-block:: c++

    INSERT INTO student (name, age) VALUES ('Cheng', 24)

当我们取出了已经存在的数据后，对其进行修改，然后重新写入数据库，即完成了一次更新操作：

.. code-block:: c++

    QSqlTableModel model;
    model.setTable("student");
    model.setFilter("age = 25");
    if (model.select()) {
        if (model.rowCount() == 1) {
            QSqlRecord record = model.record(0);
            record.setValue("age", 26);
            model.setRecord(0, record);
            model.submitAll();
        }
    }

这段代码中，我们首先找到 age = 25 的记录，然后将 age 重新设置为 26，存入相同的位置（在这里都是索引 0 的位置），提交之后完成一次更新。当然，我们也可以类似其它模型一样的设置方式：setData() 函数。具体代码片段如下：

.. code-block:: c++

    if (model.select()) {
        if (model.rowCount() == 1) {
            model.setData(model.index(0, 2), 26);
            model.submitAll();
        }
    }

注意我们的 age 列是第 3 列，索引值为 2，因为前面还有 id 和 name 两列。这里的更新操作则可以用如下 SQL 表示：

.. code-block:: c++

    UPDATE student SET age = 26 WHERE age = 25

删除操作同更新类似：

.. code-block:: c++

    QSqlTableModel model;
    model.setTable("student");
    model.setFilter("age = 25");
    if (model.select()) {
        if (model.rowCount() == 1) {
            model.removeRows(0, 1);
            model.submitAll();
        }
    }

如果使用 SQL 则是：

.. code-block:: c++

    DELETE FROM student WHERE age = 25

当我们看到 removeRows() 函数就应该想到：我们可以一次删除多行。事实也正是如此，这里不再赘述。
