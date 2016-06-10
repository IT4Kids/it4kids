#ifndef CODEGENERATOR_H
#define CODEGENERATOR_H

#include <QMap>
#include <QDir>

#include "dragelem/draggableelement.h"

class MainWindow;

class CodeGenerator
{
public:
    CodeGenerator();
    QString generateSprite(Sprite *sprite);
    QString generateSprite(const QString &name);
    void generateFiles(QDir directory);

    bool supported(const QString &ident);

private:
    struct Event
    {
        QStringList _code;
        QString _register;
    };

    QString addQuotes(const QString &str);

    QString generateCode(DraggableElement* element, int sub);
    QString indent(int indent);
    QString indentCode(QStringList *code, int indent = 0, const QString &content = QString());

    QStringList processCodeField(QJsonArray Code);
    void generateMap();

    int _indentCounter;
    QMap<QString, int> _eventCounters;

    QMap<QString, QStringList> _snippets;
    QMap<QString, Event> _events;
    QMap<QString, QStringList> _commands;
    QMap<QString, QStringList> _controls;
};
#endif // CODEGENERATOR_H
