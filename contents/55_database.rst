.. _database:

`55. 数据库操作 <http://www.devbean.net/2013/06/qt-study-road-2-database/>`_
============================================================================

:作者: 豆子

:日期: 2013年06月14日

Qt 提供了 QtSql 模块来提供平台独立的基于 SQL 的数据库操作。这里我们所说的“平台独立”，既包括操作系统平台，有包括各个数据库平台。另外，我们强调了“基于 SQL”，因为 NoSQL 数据库至今没有一个通用查询方法，所以不可能提供一种通用的 NoSQL 数据库的操作。Qt 的数据库操作还可以很方便的与 model/view 架构进行整合。通常来说，我们对数据库的操作更多地在于对数据库表的操作，而这正是 model/view 架构的长项。

Qt 使用 QSqlDatabase 表示一个数据库连接。更底层上，Qt 使用驱动（drivers）来与不同的数据库 API 进行交互。Qt 桌面版本提供了如下几种驱动：

=========  ==============
驱动       数据库
=========  ==============
QDB2       IBM DB2 (7.1 或更新版本)
QIBASE     Borland InterBase
QMYSQL     MySQL
QOCI       Oracle Call Interface Driver
QODBC      Open Database Connectivity (ODBC) – Microsoft SQL Server 及其它兼容 ODBC 的数据库
QPSQL      PostgreSQL (7.3 或更新版本)
QSQLITE2   SQLite 2
QSQLITE    SQLite 3
QSYMSQL    针对 Symbian 平台的SQLite 3
QTDS       Sybase Adaptive Server (自 Qt 4.7 起废除)
=========  ==============

不过，由于受到协议的限制，Qt 开源版本并没有提供上面所有驱动的二进制版本，而仅仅以源代码的形式提供。通常，Qt 只默认搭载 QSqlite 驱动（这个驱动实际还包括 Sqlite 数据库，也就是说，如果需要使用 Sqlite 的话，只需要该驱动即可）。我们可以选择把这些驱动作为 Qt 的一部分进行编译，也可以当作插件编译。

如果习惯于使用 SQL 语句，我们可以选择 QSqlQuery 类；如果只需要使用高层次的数据库接口（不关心 SQL 语法），我们可以选择 QSqlTableModel 和 QSqlRelationalTableModel。本章我们介绍 QSqlQuery 类，在后面的章节则介绍 QSqlTableModel 和 QSqlRelationalTableModel。

在使用时，我们可以通过

.. code-block:: c++

    QSqlDatabase::drivers();

找到系统中所有可用的数据库驱动的名字列表。我们只能使用出现在列表中的驱动。由于默认情况下，QtSql 是作为 Qt 的一个模块提供的。为了使用有关数据库的类，我们必须早 .pro 文件中添加这么一句：

.. code-block:: text

    QT += sql

这表示，我们的程序需要使用 Qt 的 core、gui 以及 sql 三个模块。注意，如果需要同时使用 Qt4 和 Qt5 编译程序，通常我们的 .pro 文件是这样的：

.. code-block:: text

    QT += core gui sql
    greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

这两句也很明确：Qt 需要加载 core、gui 和 sql 三个模块，如果主板本大于 4，则再添加 widgets 模块。

下面来看一个简单的函数：

.. code-block:: c++

    bool connect(const QString &dbName)
    {
        QSqlDatabase db = QSqlDatabase::addDatabase("QSQLITE");
    //    db.setHostName("host");
    //    db.setDatabaseName("dbname");
    //    db.setUserName("username");
    //    db.setPassword("password");
        db.setDatabaseName(dbName);
        if (!db.open()) {
            QMessageBox::critical(0, QObject::tr("Database Error"),
                                  db.lastError().text());
            return false;
        }
        return true;
    }

我们使用 connect() 函数创建一个数据库连接。我们使用 QSqlDatabase::addDatabase() 静态函数完成这一请求，也就是创建了一个 QSqlDatabase 实例。注意，数据库连接使用自己的名字进行区分，而不是数据库的名字。例如，我们可以使用下面的语句：

.. code-block:: c++

    QSqlDatabase db=QSqlDatabase::addDatabase("QSQLITE", QString("con%1").arg(dbName));

此时，我们是使用 addDatabase() 函数的第二个参数来给这个数据库连接一个名字。在这个例子中，用于区分这个数据库连接的名字是 QString(“conn%1″).arg(dbName)，而不是 “QSQLITE”。这个参数是可选的，如果不指定，系统会给出一个默认的名字 QSqlDatabase::defaultConnection，此时，Qt 会创建一个默认的连接。如果你给出的名字与已存在的名字相同，新的连接会替换掉已有的连接。通过这种设计，我们可以为一个数据库建立多个连接。

我们这里使用的是 sqlite 数据库，只需要指定数据库名字即可。如果是数据库服务器，比如 MySQL，我们还需要指定主机名、端口号、用户名和密码，这些语句使用注释进行了简单的说明。

接下来我们调用了 QSqlDatabase::open() 函数，打开这个数据库连接。通过检查 open() 函数的返回值，我们可以判断数据库是不是正确打开。

QtSql 模块中的类大多具有 lastError() 函数，用于检查最新出现的错误。如果你发现数据库操作有任何问题，应该使用这个函数进行错误的检查。这一点我们也在上面的代码中进行了体现。当然，这只是最简单的实现，一般来说，更好的设计是，不要在数据库操作中混杂界面代码（并且将这个 connect() 函数放在一个专门的数据库操作类中）。

接下来我们可以在 main() 函数中使用这个 connect() 函数：

.. code-block:: c++

    int main(int argc, char *argv[])
    {
        QApplication a(argc, argv);
        if (connect("demo.db")) {
            QSqlQuery query;
            if (!query.exec("CREATE TABLE student ("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "name VARCHAR,"
                            "age INT)")) {
                QMessageBox::critical(0, QObject::tr("Database Error"),
                                      query.lastError().text());
                return 1;
            }
        } else {
            return 1;
        }
        return a.exec();
    }

main() 函数中，我们调用这个 connect() 函数打开数据库。如果打开成功，我们通过一个 QSqlQuery 实例执行了 SQL 语句。同样，我们使用其 lastError() 函数检查了执行结果是否正确。

注意这里的 QSqlQuery 实例的创建。我们并没有指定是为哪一个数据库连接创建查询对象，此时，系统会使用默认的连接，也就是使用没有第二个参数的 addDatabase() 函数创建的那个连接（其实就是名字为 QSqlDatabase::defaultConnection 的默认连接）。如果没有这么一个连接，系统就会抱错。也就是说，如果没有默认连接，我们在创建 QSqlQuery 对象时必须指明是哪一个 QSqlDatabase 对象，也就是 addDatabase() 的返回值。

我们还可以通过使用 QSqlQuery::isActive() 函数检查语句执行正确与否。如果 QSqlQuery 对象是活动的，该函数返回 true。所谓“活动”，就是指该对象成功执行了 exec() 函数，但是还没有完成。如果需要设置为不活动的，可以使用 finish() 或者 clear() 函数，或者直接释放掉这个 QSqlQuery 对象。这里需要注意的是，如果存在一个活动的 SELECT 语句，某些数据库系统不能成功完成 connect() 或者 rollback() 函数的调用。此时，我们必须首先将活动的 SELECT 语句设置成不活动的。

创建过数据库表 student 之后，我们开始插入数据，然后将其独取出来：

.. code-block:: c++

    if (connect("demo.db")) {
        QSqlQuery query;
        query.prepare("INSERT INTO student (name, age) VALUES (?, ?)");
        QVariantList names;
        names << "Tom" << "Jack" << "Jane" << "Jerry";
        query.addBindValue(names);
        QVariantList ages;
        ages << 20 << 23 << 22 << 25;
        query.addBindValue(ages);
        if (!query.execBatch()) {
            QMessageBox::critical(0, QObject::tr("Database Error"),
                                  query.lastError().text());
        }
        query.finish();
        query.exec("SELECT name, age FROM student");
        while (query.next()) {
            QString name = query.value(0).toString();
            int age = query.value(1).toInt();
            qDebug() << name << ": " << age;
        }
    } else {
        return 1;
    }

依旧连接到我们创建的 demo.db 数据库。我们需要插入多条数据，此时可以使用 QSqlQuery::exec() 函数一条一条插入数据，但是这里我们选择了另外一种方法：批量执行。首先，我们使用 QSqlQuery::prepare() 函数对这条 SQL 语句进行预处理，问号 ? 相当于占位符，预示着以后我们可以使用实际数据替换这些位置。简单说明一下，预处理是数据库提供的一种特性，它会将 SQL 语句进行编译，性能和安全性都要优于普通的 SQL 处理。在上面的代码中，我们使用一个字符串列表 names 替换掉第一个问号的位置，一个整型列表 ages 替换掉第二个问号的位置，利用 QSqlQuery::addBindValue() 我们将实际数据绑定到这个预处理的 SQL 语句上。需要注意的是，names 和 ages 这两个列表里面的数据需要一一对应。然后我们调用 QSqlQuery::execBatch() 批量执行 SQL，之后结束该对象。这样，插入操作便完成了。

另外说明一点，我们这里使用了 ODBC 风格的 ? 占位符，同样，我们也可以使用 Oracle 风格的占位符：

.. code-block:: c++

    query.prepare("INSERT INTO student (name, age) VALUES (:name, :age)");

此时，我们就需要使用

.. code-block:: c++

    query.bindValue(":name", names);
    query.bindValue(":age", ages);

进行绑定。Oracle 风格的绑定最大的好处是，绑定的名字和值很清晰，与顺序无关。但是这里需要注意，bindValue() 函数只能绑定一个位置。比如

.. code-block:: c++

    query.prepare("INSERT INTO test (name1, name2) VALUES (:name, :name)");
    // ...
    query.bindValue(":name", name);

只能绑定第一个 :name 占位符，不能绑定到第二个。

接下来我们依旧使用同一个查询对象执行一个 SELECT 语句。如果存在查询结果，QSqlQuery::next() 会返回 true，直到到达结果最末，返回 false，说明遍历结束。我们利用这一点，使用 while 循环即可遍历查询结果。使用 QSqlQuery::value() 函数即可按照 SELECT 语句的字段顺序获取到对应的数据库存储的数据。

对于数据库事务的操作，我们可以使用 QSqlDatabase::transaction() 开启事务，QSqlDatabase::commit() 或者 QSqlDatabase::rollback() 结束事务。使用 QSqlDatabase::database() 函数则可以根据名字获取所需要的数据库连接。
