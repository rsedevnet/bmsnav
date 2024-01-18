import { QMainWindow, QWidget, QLabel, FlexLayout, QPushButton, QIcon } from '@nodegui/nodegui';

const win = new QMainWindow();
win.setWindowTitle('BMSNavServer');

const rootWidget = new QWidget();
rootWidget.setObjectName('root');

const rootLayout = new FlexLayout();
rootWidget.setLayout(rootLayout);

const label = new QLabel();
label.setObjectName('ramp-start');
label.setText('Ramp Start');

const button = new QPushButton();
button.setText('GO!');

rootLayout.addWidget(label);
rootLayout.addWidget(button);

win.setCentralWidget(rootWidget);
win.setStyleSheet(
`
  #root {
    background-color: rgb(42,41,39);;
    height: '100%';
    align-items: 'center';
    justify-content: 'center';
  }
  #ramp-start {
    font-size: 16px;
    font-weight: bold;
    padding: 1;
  }
`);

win.show();

(global as any).win = win;
