#include <QApplication>
#include <QPainter>

#include "dragelem/draggableelement.h"
#include "paramdock.h"
#include "sprite.h"

DockWidget::DockWidget(QColor color, Sprite *sprite, QWidget *parent) : QWidget(parent), DockingArea(sprite)
{
    _color = color.darker(130);

    _path.moveTo(0, 6);
    _path.lineTo(6, 0);
    _path.lineTo(18, 0);
    _path.lineTo(24,6);
    _path.lineTo(18, 12);
    _path.lineTo(6, 12);
    _path.lineTo(0, 6);
    setFixedSize(24, 12);
}

void DockWidget::dock(DraggableElement* dragElem)
{
    // TODO: rework this
    if(dragElem != parent())
    {
        QString elemClass(dragElem->metaObject()->className());
        if(elemClass == "PredicateDE")
        {
            _dockedElem = dragElem;
            _dockedElem->setCurrentDock(this);
            int index = ((QBoxLayout*) (parentWidget()->layout()))->indexOf(this);
            ((QBoxLayout*) (parentWidget()->layout()))->removeWidget(this);
            ((QBoxLayout*) (parentWidget()->layout()))->insertWidget(index, _dockedElem);
            _dockedElem->setParent(parentWidget());
            _dockedElem->show();
            hide();
            QString className(parentWidget()->metaObject()->className());
            if(className == "QWidget")
            {
                ((DraggableElement*) parentWidget()->parentWidget())->resize();
                ((DraggableElement*) parentWidget()->parentWidget())->show();
            }
            else
            {
                ((DraggableElement*) parentWidget())->resize();
                ((DraggableElement*) parentWidget())->show();
            }
        }
    }
    // TODO: reload the code
}

void DockWidget::undock()
{
    int index = ((QBoxLayout*) (parentWidget()->layout()))->indexOf(_dockedElem);
    ((QBoxLayout*) (parentWidget()->layout()))->removeWidget(_dockedElem);
    QPoint pos = _dockedElem->mapToGlobal(_dockedElem->pos());
    _dockedElem->setCurrentDock(0);
    _dockedElem->setParent(QApplication::activeWindow());
    _dockedElem->move(_dockedElem->mapFromGlobal(pos));
    _dockedElem->show();
    ((QBoxLayout*) (parentWidget()->layout()))->insertWidget(index, this);
    show();
    QString className(parentWidget()->metaObject()->className());
    if(className == "QWidget")
    {
        ((DraggableElement*) parentWidget()->parentWidget())->resize();
        ((DraggableElement*) parentWidget()->parentWidget())->resize();
        ((DraggableElement*) parentWidget()->parentWidget())->show();
    }
    else
    {
        ((DraggableElement*) parentWidget())->resize();
        ((DraggableElement*) parentWidget())->resize();
        ((DraggableElement*) parentWidget())->show();
    }
}

DockWidget::~DockWidget()
{
}

void DockWidget::paintEvent(QPaintEvent*)
{
    QPainter painter(this);

    // style(), width(), brush(), capStyle() and joinStyle().
    QPen pen(QColor(_color), 0, Qt::SolidLine, Qt::SquareCap, Qt::RoundJoin);
    painter.setPen(pen);

    // Brush
    QBrush brush;
    brush.setColor(QColor(_color));
    brush.setStyle(Qt::SolidPattern);

    // Draw polygon
    painter.fillPath(_path, brush);
    painter.setBackgroundMode(Qt::TransparentMode);
    setRect(QRect(mapToGlobal(QPoint(0, 0)), QSize(24, 12)));
}

QString DockWidget::getDockedElemIdent() const
{
    // TODO
    if(_dockedElem) return _dockedElem->getIdentifier();
    return "empty";
}

ParamDock::ParamDock(QColor color, Sprite *sprite, QWidget *parent) : _dockWidget(new DockWidget(color, sprite, parent))
{
}

ParamDock::~ParamDock()
{
}

QString ParamDock::getString() const
{
    return _dockWidget->getDockedElemIdent();
}

