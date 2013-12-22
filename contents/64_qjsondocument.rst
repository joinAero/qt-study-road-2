.. _qjsondocument:

`64. 使用 QJsonDocument 处理 JSON <http://www.devbean.net/2013/09/qt-study-road-2-qjsondocument/>`_
===================================================================================================

:作者: 豆子

:日期: 2013年09月23日

上一章我们了解了如何使用 QJson 处理 JSON 文档。QJson 是一个基于 Qt 的第三方库，适用于 Qt4 和 Qt5 两个版本。不过，如果你的应用仅仅需要考虑兼容 Qt5，其实已经有了内置的处理函数。Qt5 新增加了处理 JSON 的类，与 XML 类库类似，均以 QJson 开头，在 QtCore 模块中，不需要额外引入其它模块。Qt5 新增加六个相关类：

===================== =====================
QJsonArray            封装 JSON 数组
QJsonDocument         读写 JSON 文档
QJsonObject           封装 JSON 对象
QJsonObject::iterator 用于遍历QJsonObject的 STL 风格的非 const 遍历器
QJsonParseError       报告 JSON 处理过程中出现的错误
QJsonValue            封装 JSON 值
===================== =====================

我们还是使用前一章的 JSON 文档，这次换用QJsonDocument 来解析。注意，QJsonDocument要求使用 Qt5，本章中所有代码都必须在 Qt5 环境下进行编译运行。

.. code-block:: c++

    QString json("{"
            "\"encoding\" : \"UTF-8\","
            "\"plug-ins\" : ["
            "\"python\","
            "\"c++\","
            "\"ruby\""
            "],"
            "\"indent\" : { \"length\" : 3, \"use_space\" : true }"
            "}");
    QJsonParseError error;
    QJsonDocument jsonDocument = QJsonDocument::fromJson(json.toUtf8(), &error);
    if (error.error == QJsonParseError::NoError) {
        if (jsonDocument.isObject()) {
            QVariantMap result = jsonDocument.toVariant().toMap();
            qDebug() << "encoding:" << result["encoding"].toString();
            qDebug() << "plugins:";

            foreach (QVariant plugin, result["plug-ins"].toList()) {
                qDebug() << "\t-" << plugin.toString();
            }

            QVariantMap nestedMap = result["indent"].toMap();
            qDebug() << "length:" << nestedMap["length"].toInt();
            qDebug() << "use_space:" << nestedMap["use_space"].toBool();
        }
    } else {
        qFatal(error.errorString().toUtf8().constData());
        exit(1);
    }

这段代码与前面的几乎相同。QJsonDocument::fromJson()可以由QByteArray对象构造一个QJsonDocument对象，用于我们的读写操作。这里我们传入一个QJsonParseError对象的指针作为第二个参数，用于获取解析的结果。如果QJsonParseError::error()的返回值为QJsonParseError::NoError，说明一切正常，则继续以QVariant的格式进行解析（由于我们知道这是一个 JSON 对象，因此只判断了isObject()。当处理未知的 JSON 时，或许应当将所有的情况都考虑一边，包括isObject()、isArray()以及isEmpty()）。

也就是说，如果需要使用QJsonDocument处理 JSON 文档，我们只需要使用下面的代码模板：

.. code-block:: c++

    // 1. 创建 QJsonParseError 对象，用来获取解析结果
    QJsonParseError error;
    // 2. 使用静态函数获取 QJsonDocument 对象
    QJsonDocument jsonDocument = QJsonDocument::fromJson(json.toUtf8(), &error);
    // 3. 根据解析结果进行处理
    if (error.error == QJsonParseError::NoError) {
        if (!(jsonDocument.isNull() || jsonDocument.isEmpty())) {
            if (jsonDocument.isObject()) {
                // ...
            } else if (jsonDocument.isArray()) {
                // ...
            }
        }
    } else {
        // 检查错误类型
    }

将QVariant对象生成 JSON 文档也很简单：

.. code-block:: c++

    QVariantList people;
     
    QVariantMap bob;
    bob.insert("Name", "Bob");
    bob.insert("Phonenumber", 123);
     
    QVariantMap alice;
    alice.insert("Name", "Alice");
    alice.insert("Phonenumber", 321);
     
    people << bob << alice;
     
    QJsonDocument jsonDocument = QJsonDocument::fromVariant(people);
    if (!jsonDocument.isNull()) {
        qDebug() << jsonDocument.toJson();
    }

这里我们仍然使用的是QJsonDocument，只不过这次我们需要使用QJsonDocument::fromVariant()函数获取QJsonDocument对象。QJsonDocument也可以以二进制格式读取对象，比如QJsonDocument::fromBinaryData()和QJsonDocument::fromRawData()函数。当我们成功获取到QJsonDocument对象之后，可以使用toJson()生成 JSON 文档。

以上介绍了当我们有一个 JSON 文档时，如何使用QJsonDocument进行处理。如果我们没有 JSON 文档，那么我们可以使用QJsonDocument的setArray()和setObject()函数动态设置该对象，然后再生成对应的 JSON 格式文档。不过这部分需求比较罕见，因为我们直接可以从QVariant值类型获取。

Qt5 提供的 JSON 类库直接支持 :ref:`隐式数据共享 <implicit_sharing>` ，因此我们不需要为复制的效率担心。
