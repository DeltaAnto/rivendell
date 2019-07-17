// rdlogmanager.h
//
// The Log Manager Utility for Rivendell.
//
//   (C) Copyright 2002-2015 Fred Gleason <fredg@paravelsystems.com>
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

#ifndef RDLOGMANAGER_H
#define RDLOGMANAGER_H

#include <qwidget.h>
#include <qsize.h>
#include <qsizepolicy.h>
#include <qlabel.h>
#include <q3listview.h>
#include <qpushbutton.h>
#include <qpixmap.h>

#include <rdlog_line.h>

#define RDLOGMANAGER_USAGE "[OPTIONS]\n"

//
// Command Line Operations
//
extern int RunLogOperation(int argc,char *argv[],const QString &svcname,
			   int start_offset,bool protect_existing,bool gen_log,
			   bool merge_mus,bool merge_tfc);
extern int RunReportOperation(int argc,char *argv[],const QString &rptname,
			      bool protect_existing,int start_offset,
			      int end_offset);

class MainWidget : public QWidget
{
 Q_OBJECT
 public:
  MainWidget(QWidget *parent=0);
  QSize sizeHint() const;
  QSizePolicy sizePolicy() const;
  
 private slots:
  void userData();
  void eventsData();
  void clocksData();
  void gridsData();
  void generateData();
  void reportsData();
  void quitMainWidget();

 private:
  void LoadConfig();
  //  QSqlDatabase *log_db;
  QString log_filename;
  QLabel *log_user_label;
  QPushButton *log_events_button;
  QPushButton *log_clocks_button;
  QPushButton *log_grids_button;
  QPushButton *log_logs_button;
  QPushButton *log_reports_button;
  QPushButton *log_close_button;
  QPixmap *log_rivendell_map;
};


#endif  // RDLOGMANAGER_H
