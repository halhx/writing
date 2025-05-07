def run():
    # load iris dataset
    from sklearn import datasets
    iris = datasets.load_iris()

    features = iris.data
    labels = iris.target


    # inspect the dataset
    from tabulate import tabulate
    from random import sample
    iris_sample = []
    for i in sample(range(iris.data.shape[0]), 10):
      row = list(features[i]) + [labels[i]]
      iris_sample.append(row)
    print(tabulate(iris_sample, headers=iris.feature_names + ['species']))


    # visualize the dataset
    import matplotlib.pyplot as plt
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    for species, target_name in enumerate(iris.target_names):
        X_plot = features[labels == species]
        plt.plot(X_plot[:, 0], X_plot[:, 1], linestyle='none', marker='o', label=target_name)
    plt.xlabel(iris.feature_names[0])
    plt.ylabel(iris.feature_names[1])
    plt.axis('equal')
    plt.legend()

    plt.subplot(1, 2, 2)
    for species, target_name in enumerate(iris.target_names):
        X_plot = features[labels == species]
        plt.plot(X_plot[:, 2], X_plot[:, 3], linestyle='none', marker='o', label=target_name)
    plt.xlabel(iris.feature_names[2])
    plt.ylabel(iris.feature_names[3])
    plt.axis('equal')
    plt.legend()

    # split data into train and validation sets
    from sklearn.model_selection import train_test_split
    x_train, x_validation, y_train, y_validation = train_test_split(features, labels, test_size=0.4, random_state=0)

    # define a model
    from sklearn.neighbors import KNeighborsClassifier
    model = KNeighborsClassifier(n_neighbors=5)

    # train the model with the train data set
    model.fit(x_train, y_train)

    # now that the model is trained, let's use it to make prediction
    y_prediction = model.predict(x_validation)

    # how good were the predictions?
    from sklearn.metrics import accuracy_score, classification_report
    print(accuracy_score(y_validation, y_prediction))
    print(classification_report(y_validation, y_prediction))

    # let's see the model performance visually
    from sklearn.metrics import confusion_matrix, plot_confusion_matrix
    confusion_matrix(y_validation, y_prediction)
    plot_confusion_matrix(model, x_validation, y_validation, cmap=plt.cm.Blues)
    plt.show()
