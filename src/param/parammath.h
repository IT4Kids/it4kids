#ifndef PARAMMATH_H
#define PARAMMATH_H

#include <QComboBox>

#include "param.h"

class ParamMath : public QComboBox, public ParamBase
{
    Q_OBJECT
public:
    ParamMath(QWidget* parent);
    ~ParamMath();

    QString getValue() const;
};

#endif // PARAMMATH_H
