.. _edit_sql_fk:

`58. 编辑数据库外键 <http://www.devbean.net/2013/07/qt-study-road-2-edit-sql-fk/>`_
===================================================================================

:作者: 豆子

:日期: 2013年07月12日

前面几章我们介绍了如何对数据库进行操作以及如何使用图形界面展示数据库数据。本章我们将介绍如何对数据库的数据进行编辑。当然，我们可以选择直接使用 SQL 语句进行更新，这一点同前面所说的 model/view 的编辑没有什么区别。除此之外，Qt 还为图形界面提供了更方便的展示并编辑的功能。


普通数据的编辑很简单，这里不再赘述。不过，我们通常会遇到多个表之间存在关联的情况。首先我们要提供一个 city 表：

.. code-block:: c++

    CREATE TABLE city (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR);
     
    INSERT INTO city (name) VALUES ('Beijing');
    INSERT INTO city (name) VALUES ('Shanghai');
    INSERT INTO city (name) VALUES ('Nanjing');
    INSERT INTO city (name) VALUES ('Tianjin');
    INSERT INTO city (name) VALUES ('Wuhan');
    INSERT INTO city (name) VALUES ('Hangzhou');
    INSERT INTO city (name) VALUES ('Suzhou');
    INSERT INTO city (name) VALUES ('Guangzhou');

由于 city 表是一个参数表，所以我们直接将所需要的城市名称直接插入到表中。接下来我们创建 student 表，并且使用外键连接 city 表：

.. code-block:: c++

    CREATE TABLE student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        age INTEGER,
        address INTEGER,
        FOREIGN KEY(address) REFERENCES city(id));

我们重新创建 student 表（如果你使用的 RDBMS 支持 ALTER TABLE 语句直接修改表结构，就不需要重新创建了；否则的话只能先删除旧的表，再创建新的表，例如 sqlite）。

这里需要注意一点，如果此时我们在 Qt 中直接使用

.. code-block:: c++

    INSERT INTO student (name, age, address) VALUES ('Tom', 24, 100);

语句，尽管我们的 city 中没有 ID 为 100 的记录，但还是是可以成功插入的。这是因为虽然 Qt 中的 sqlite 使用的是支持外键的 sqlite3，但 Qt 将外键屏蔽掉了。为了启用外键，我们需要首先使用 QSqlQuery 执行：

.. code-block:: c++

    PRAGMA foreign_keys = ON;

然后就会发现这条语句不能成功插入了。接下来我们插入一些正常的数据：

.. code-block:: c++

    INSERT INTO student (name, age, address) VALUES ('Tom', 20, 2);
    INSERT INTO student (name, age, address) VALUES ('Jack', 23, 1);
    INSERT INTO student (name, age, address) VALUES ('Jane', 22, 4);
    INSERT INTO student (name, age, address) VALUES ('Jerry', 25, 5);

下面，我们使用 model/view 方式来显示数据：

.. code-block:: c++

    QSqlTableModel *model = new QSqlTableModel(this);
    model->setTable("student");
    model->setSort(ColumnID_Name, Qt::AscendingOrder);
    model->setHeaderData(ColumnID_Name, Qt::Horizontal, "Name");
    model->setHeaderData(ColumnID_Age, Qt::Horizontal, "Age");
    model->setHeaderData(ColumnID_City, Qt::Horizontal, "City");
    model->select();
     
    QTableView *view = new QTableView(this);
    view->setModel(model);
    view->setSelectionMode(QAbstractItemView::SingleSelection);
    view->setSelectionBehavior(QAbstractItemView::SelectRows);
    view->resizeColumnsToContents();
     
    QHeaderView *header = view->horizontalHeader();
    header->setStretchLastSection(true);

这段代码和我们前面见到的没有什么区别。我们可以将其补充完整后运行一下看看：

.. admonition:: 带有外键的数据库数据的显示

    .. image:: imgs/58/sql-data.png

注意外键部分：City 一列仅显示出了我们保存的外键。如果我们使用 QSqlQuery，这些都不是问题，我们可以将外键信息放在一个 SQL 语句中 SELECT 出来。但是，我们不想使用 QSqlQuery，那么现在可以使用另外的一个模型：QSqlRelationalTableModel。QSqlRelationalTableModel 与 QSqlTableModel 十分类似，可以为一个数据库表提供可编辑的数据模型，同时带有外键的支持。下面我们修改一下我们的代码：

.. code-block:: c++

    QSqlRelationalTableModel *model = new QSqlRelationalTableModel(this);
    model->setTable("student");
    model->setSort(ColumnID_Name, Qt::AscendingOrder);
    model->setHeaderData(ColumnID_Name, Qt::Horizontal, "Name");
    model->setHeaderData(ColumnID_Age, Qt::Horizontal, "Age");
    model->setHeaderData(ColumnID_City, Qt::Horizontal, "City");
    model->setRelation(ColumnID_City, QSqlRelation("city", "id", "name"));
    model->select();
     
    QTableView *view = new QTableView(this);
    view->setModel(model);
    view->setSelectionMode(QAbstractItemView::SingleSelection);
    view->setSelectionBehavior(QAbstractItemView::SelectRows);
    view->resizeColumnsToContents();
    view->setItemDelegate(new QSqlRelationalDelegate(view));
     
    QHeaderView *header = view->horizontalHeader();
    header->setStretchLastSection(true);

这段代码同前面的几乎一样。我们首先创建一个 QSqlRelationalTableModel 对象。注意，这里我们有一个 setRelation() 函数的调用。该语句说明，我们将第 ColumnID_City 列作为外键，参照于 city 表的 id 字段，使用 name 进行显示。另外的 setItemDelegate() 语句则提供了一种用于编辑外键的方式。运行一下程序看看效果：

.. admonition:: 直接显示外键

    .. image:: imgs/58/sql-data-2.png

此时，我们的外键列已经显示为 city 表的 name 字段的实际值。同时在编辑时，系统会自动成为一个 QComboBox 供我们选择。当然，我们需要自己将选择的外键值保存到实际记录中，这部分我们前面已经有所了解。
