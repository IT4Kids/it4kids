#include "codegenerator.h"
#include "sprite.h"
#include "mainwindow.h"
#include <qfile.h>

CodeGenerator::CodeGenerator(MainWindow * main)
{
    _Mainwindow = main;
    generateMap();
}

void CodeGenerator::generateFile(){
    QString str = "";
    SpriteVector* spriteVec = _Mainwindow->getSpriteVector();

    //every Sprite
    for(SpriteVector::iterator it = spriteVec->begin(); it != spriteVec->end(); ++it)
    {
        //create class file
        str += "class " + (*it)->getName() + "(Entity):\n";

        //check every block for "header"-Block
        DragElemVector * eleVec = (*it)->getDragElemVector();
        for(DragElemVector::iterator it2 = eleVec->begin(); it2 != eleVec->end(); ++it2)
        {
            //prüfe ob start Command
            if ((*it2)->getType() == "hat")
            {
                str += generateCode(*it2,1);
                //generateCode(*it2,0);
                //qDebug() << generateCode(*it2,0);
            }
        }
        str += "\n";
    }

    //write to file
    QFile file("out.txt");
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text))
        return;

    QTextStream out(&file);
    out << str;

    file.close();
}


QString CodeGenerator::generateCode(DragableElement* element, int sub)
{
    DragableElement* next = element;
        QString ret = "";
        ArgumentStruct* argument;
        //int sublvl = sub;
        while (next != (void*)0)
        {
            //add command
            argument = next->getArguments();
            ret += subident(sub) + dict(argument) + "\n";

            //add sub Command, if exists
            if (next->getWrapElem() != (void*)0)
            {
                 ret += generateCode(next->getWrapElem(),sub+1); //todo dict start und end
            }

            next = next->getNextElem();
        }
        return ret;
}

//einrückungen etc.
QString CodeGenerator::subident(int sub)
{
    QString str ="";
    for (int i = 0; i<sub;i++)
    {
        str += "    ";//map["tab"];
    }
    return str;
}

//translate ccommand in reqired language
//uses special commands :start, end, tab
QString CodeGenerator::dict(ArgumentStruct* argument)
{
    QString str;
    if (map.contains(argument->name))
    {
       if (!argument->type)
           str += subident(1);
       str += map[argument->name];
    }else{
        qDebug() << "block: " << argument->name << "not supportet jet";
        str = subident(1) + "NSE: " + argument->name;
    }

    str.replace("%1",argument->arg1);
    str.replace("%2",argument->arg2);
    str.replace("%3",argument->arg3);
    str.replace("%4",argument->arg4);
    str.replace("%5",argument->arg5);

    return str;
}

void CodeGenerator::generateMap()
{
    QFile file("..\\it4kids\\src\\in.txt");
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
    {
        qDebug() << "Python datei konnte nicht geladen werden";
        return;
    }
    int n = 0;
    int err = 0;

    while (!file.atEnd()) {
        QString line = file.readLine();
        line.replace("\n","");

        QStringList list = line.split("@@",QString::SkipEmptyParts);

        if (list.length() == 2)
        {
            map.insert(list[0], list[1]);

        }
        else
        {
            qDebug() << "invalide command line: " << line;
            err++;
        }
        n++;
    }
    qDebug() << n-err << "/" << n << "lines loadet";
}
