.. _qjson:

`63. 使用 QJson 处理 JSON <http://www.devbean.net/2013/09/qt-study-road-2-qjson/>`_
===================================================================================

:作者: 豆子

:日期: 2013年09月09日

XML 曾经是各种应用的配置和传输的首选方式。但是现在 XML 遇到了一个强劲的对手：JSON。我们可以在这里看到有关 JSON 的语法。总体来说，JSON 的数据比 XML 更紧凑，在传输效率上也要优于 XML。不过 JSON 数据的层次化表达不及 XML，至少不如 XML 那样突出。不过这并不会阻止 JSON 的广泛应用。

一个典型的 JSON 文档可以像下面的例子：

.. code-block:: json

    {
      "encoding" : "UTF-8",
      "plug-ins" : [
          "python",
          "c++",
          "ruby"
          ],
      "indent" : { "length" : 3, "use_space" : true }
    }

JSON 的全称是 JavaScript Object Notation，与 JavaScript 密不可分。熟悉 JavaScript 的童鞋马上就会发现，JSON 的语法就是 JavaScript 对象声明的语法。JSON 文档其实就是一个 JavaScript 对象，因而也称为 JSON 对象，以大括号作为起止符，其实质是不排序的键值对，其中键要求是 string 类型，值可以是任意类型。比如上面的示例，键 encoding 的值是字符串 UTF-8；键 plug-ins 的值是一个数组类型，在 JSON 中，数组以中括号表示，这个数组是一个字符串列表，分别有 python、c++ 和 ruby 三个对象；键 indent 的值是一个对象，这个对象有两个属性，length = 3，use_space = true。

对于 JSON 的解析，我们可以使用 QJson 这个第三方库。QJson 可以将 JSON 数据转换为 QVariant 对象，将 JSON 数组转换成 QVariantList 对象，将 JSON 对象转换成 QVariantMap 对象。我们在这里使用 git clone 出 QJson 的整个代码。注意 QJson 没有提供链接库的 pro 文件，因此我们只需要将所有源代码文件添加到我们的项目即可（如同这些文件是我们自己写的一样）。接下来就可以使用 QJson 读取 JSON 内容：

.. code-block:: c++

    #include "parser.h"
    //////////
    QJson::Parser parser;
    bool ok;
     
    QString json("{"
            "\"encoding\" : \"UTF-8\","
            "\"plug-ins\" : ["
            "\"python\","
            "\"c++\","
            "\"ruby\""
            "],"
            "\"indent\" : { \"length\" : 3, \"use_space\" : true }"
            "}");
    QVariantMap result = parser.parse(json.toUtf8(), &ok).toMap();
    if (!ok) {
        qFatal("An error occurred during parsing");
        exit (1);
    }
     
    qDebug() << "encoding:" << result["encoding"].toString();
    qDebug() << "plugins:";
     
    foreach (QVariant plugin, result["plug-ins"].toList()) {
        qDebug() << "\t-" << plugin.toString();
    }
     
    QVariantMap nestedMap = result["indent"].toMap();
    qDebug() << "length:" << nestedMap["length"].toInt();
    qDebug() << "use_space:" << nestedMap["use_space"].toBool();

将 JSON 对象转换成QVariant对象很简单，基本只需要下面几行：

.. code-block:: c++

    // 1. 创建 QJson::Parser 对象
    QJson::Parser parser;
     
    bool ok;
    // 2. 将 JSON 对象保存在一个对象 json 中，进行数据转换
    QVariant result = parser.parse (json, &ok);

QJson::Parser::parse()函数接受两个参数，第一个参数是 JSON 对象，可以是QIODevice \*或者是QByteArray；第二个参数是转换成功与否，如果成功则被设置为 true。函数返回转换后的QVariant对象。注意我们转换后的对象其实是一个QVariantMap类型，可以像QMap一样使用重载的 [] 获取键所对应的值。另外，由于 result["plug-ins"] 是一个QVariantList对象（因为是由 JSON 数组返回的），因而可以调用其toList()函数，通过遍历输出每一个值。

如果需要将QVariant生成 JSON 对象，我们则使用QJson::Serializer对象。例如：

.. code-block:: c++

    QVariantList people;
     
    QVariantMap bob;
    bob.insert("Name", "Bob");
    bob.insert("Phonenumber", 123);
     
    QVariantMap alice;
    alice.insert("Name", "Alice");
    alice.insert("Phonenumber", 321);
     
    people << bob << alice;
     
    QJson::Serializer serializer;
    bool ok;
    QByteArray json = serializer.serialize(people, &ok);
     
    if (ok) {
        qDebug() << json;
    } else {
        qCritical() << "Something went wrong:" << serializer.errorMessage();
    }

QJson::Serializer和前面的QJson::Parser的用法相似，只需要调用QJson::Serializer::serialize()即可将QVariant类型的数据转换为 JSON 格式。其返回值是QByteArray类型，可以用于很多其它场合。

上面是 QJson 的主要使用方法。其实 QJson 还提供了另外一个类QObjectHelper，用于QVariant和QObject之间的转换。注意我们上面所说的 QJson 的转换需要的是QVariant类型的数据，无论是转换到 JSON 还是从 JSON 转换而来。但是通常我们在应用程序中使用的是QObject及其子类。QObjectHelper提供了一个工具函数，完成QVariant和QObject之间的转换。例如我们有下面的类：

.. code-block:: c++

    class Person : public QObject
    {
      Q_OBJECT
     
      Q_PROPERTY(QString name READ name WRITE setName)
      Q_PROPERTY(int phoneNumber READ phoneNumber WRITE setPhoneNumber)
      Q_PROPERTY(Gender gender READ gender WRITE setGender)
      Q_PROPERTY(QDate brithday READ brithday WRITE setBrithday)
      Q_ENUMS(Gender)
     
      public:
        Person(QObject* parent = 0);
        ~Person();
     
        QString name() const;
        void setName(const QString& name);
     
        int phoneNumber() const;
        void setPhoneNumber(const int phoneNumber);
     
        enum Gender {Male, Female};
        void setGender(Gender gender);
        Gender gender() const;
     
        QDate brithday() const;
        void setBrithday(const QDate& dob);
     
      private:
        QString m_name;
        int m_phoneNumber;
        Gender m_gender;
        QDate m_dob;
    };

那么，我们可以使用下面的代码将Person类进行 JSON 序列化：

.. code-block:: c++

    Person person;
    person.setName("Flavio");
    person.setPhoneNumber(123456);
    person.setGender(Person::Male);
    person.setDob(QDate(1982, 7, 12));
     
    QVariantMap variant = QObjectHelper::qobject2qvariant(&person);
    QJson::Serializer serializer;
    qDebug() << serializer.serialize( variant);

以及：

.. code-block:: c++

    QJson::Parser parser;
    QVariant variant = parser.parse(json);
    Person person;
    QObjectHelper::qvariant2qobject(variant.toMap(), &person);

进行反序列化。
