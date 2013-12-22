.. _access_network_4:

.. raw:: html

    <style> .red { color: red } </style>

.. role:: red

`68. 访问网络（4） <http://www.devbean.net/2013/11/qt-study-road-2-access-network-4/>`_
=======================================================================================

:作者: 豆子

:日期: 2013年11月07日

前面几章我们了解了如何使用QNetworkAccessManager 访问网络。在此基础上，我们已经实现了一个简单的查看天气的程序。在这个程序中，我们使用QNetworkAccessManager进行网络的访问，从一个网络 API 获取某个城市的当前天气状况。

如果你仔细观察就会发现，即便我们没有添加任何相关代码，QNetworkAccessManager的网络访问并不会阻塞 GUI 界面。也就是说，即便是在进行网络访问的时候，我们的界面还是可以响应的。相比之下，如果你对 Java 熟悉，就会了解到，在 Java 中，进行 Socket 通讯时，界面默认是阻塞的，当程序进行网络访问操作时，界面不能对我们的操作做出任何响应。由此可以看出，QNetworkAccessManager的网络访问默认就是异步的、非阻塞的。这样的实现固然很好，也符合大多数程序的应用情形：我们当然希望程序界面能够始终对用户操作做出响应。不过，在某些情况下，我们还是希望会有一些同步的网络操作。典型的是登录操作。在登录时，我们必须要等待网络返回结果，才能让界面做出响应：是验证成功进入系统，还是验证失败做出提示？这就是本章的主要内容：如何使用QNetworkAccessManager进行同步网络访问。

当我们重新运行先前编译好的程序，可以看看这样一个操作：由于我们的界面是不阻塞的，那么当我们第一次点击了 Refresh 按钮之后，马上切换城市再点击一次 Refresh 按钮，就会看到第一次的返回结果一闪而过。这是因为第一次网络请求尚未完成时，用户又发送了一次请求，Qt 会将两次请求的返回结果顺序显示。这样处理结果可能会出现与预期不一致的情况（比如第一次请求响应由于某种原因异常缓慢，第二次却很快，此时第二次结果会比第一次先到，那么很明显，当第一次结果返回时，第二次的结果就会被覆盖掉。我们假设认为用户需要第二次的返回，那么就会出现异常）。

要解决这种情况，我们可以在有网络请求时将界面锁死，不允许用户进行更多的操作（更好的方法是仅仅锁住某些按钮，而不是整个界面。不过这里我们以锁住整个界面为例）。我们的解决方案很简单：当QNetworkAccessManager发出请求之后，我们进入一个新的事件循环，将操作进行阻塞。我们的代码示例如下：

.. code-block:: c++

    void fetchWeather(const QString &cityName)
    {
        QEventLoop eventLoop;
        connect(netWorker, &NetWorker::finished,
                &eventLoop, &QEventLoop::quit);
        QNetworkReply *reply = netWorker->get(QString("http://api.openweathermap.org/data/2.5/weather?q=%1&mode=json&units=metric&lang=zh_cn").arg(cityName));
        replyMap.insert(reply, FetchWeatherInfo);
        eventLoop.exec();
    }

注意，我们在函数中创建了一个QEventLoop实例，将其quit()与NetWorker::finished()信号连接起来。当NetWorker::finished()信号发出时，QEventLoop::quit()就会被调用。在NetWorker::get()执行之后，调用QEventLoop::exec()函数开始事件循环。此时界面就是被阻塞。

现在我们只是提供了一种很简单的思路。当然这并不是最好的思路：程序界面直接被阻塞，用户获得不了任何提示，会误以为程序死掉。更好的做法是做一个恰当的提示，不过这已经超出我们本章的范畴。更重要的是，这种思路并不完美。 :red:`如果你的程序是控制台程序（没有 GUI 界面），或者是某些特殊的情况下，会造出死锁！` 控制台程序中发送死锁的原因在于在非 GUI 程序中另外启动事件循环会将主线程阻塞，QNetworkAccessManager的所有信号都不会收到。“某些特殊的情况”，我们会在后面有关线程的章节详细解释。不过，要完美解决这个问题，我们必须使用另外的线程。 `这里 <http://www.codeproject.com/Articles/484905/Use-QNetworkAccessManager-for-synchronous-download>`_ 有一个通用的解决方案，感兴趣的童鞋可以详细了解下。
