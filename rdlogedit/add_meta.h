// add_meta.h
//
// Add a Rivendell RDCatch Event
//
//   (C) Copyright 2018-2019 Fred Gleason <fredg@paravelsystems.com>
//
//   This program is free software; you can redistribute it and/or modify
//   it under the terms of the GNU General Public License version 2 as
//   published by the Free Software Foundation.
//
//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.
//
//   You should have received a copy of the GNU General Public
//   License along with this program; if not, write to the Free Software
//   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
//

#ifndef ADD_META_H
#define ADD_META_H

#include <qlabel.h>

#include <rddialog.h>

class AddMeta : public RDDialog
{
  Q_OBJECT
 public:
  AddMeta(QWidget *parent=0);
  ~AddMeta();
  QSize sizeHint() const;
  QSizePolicy sizePolicy() const;

 protected:
  void closeEvent(QCloseEvent *e);

 private slots:
  void markerData();
  void chainData();
  void trackData();
  void cancelData();
};


#endif

