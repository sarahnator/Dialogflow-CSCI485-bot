DROP DATABASE IF EXISTS HeadacheBot;
CREATE DATABASE HeadacheBot;
USE HeadacheBot;

CREATE TABLE question (
	QID INT NOT NULL AUTO_INCREMENT,
    qText VARCHAR (256),
		PRIMARY KEY (QID)); 

CREATE TABLE leads_to (
	parentQID INT,
    childQID INT,	
    response VARCHAR (256),
		PRIMARY KEY (parentQID, childQID),
		FOREIGN KEY (parentQID) REFERENCES question (QID),
		FOREIGN KEY (childQID) REFERENCES question (QID)); 

-- how would we generate training phrases?
CREATE TABLE DFintent (
	IID INT NOT NULL AUTO_INCREMENT,
    response VARCHAR (256),
    inputCtx JSON,
    outputCtx JSON,
    params JSON,
    fullfillment JSON,-- added
    isConversationEnd BOOL, -- added
    isDuplicate BOOL,
    dfEvent JSON,
    dfAction JSON,
    trainingPhrase JSON,
		PRIMARY KEY (IID));
    
CREATE TABLE DFleads_to (
	parentIID INT,
    childIID INT,	
		PRIMARY KEY (parentIID, childIID),
		FOREIGN KEY (parentIID) REFERENCES DFintent (IID),
		FOREIGN KEY (childIID) REFERENCES DFintent (IID)); 

CREATE TABLE corresponds_to (
	QID INT,
    IID INT,
		PRIMARY KEY (QID, IID),
        FOREIGN KEY (QID) REFERENCES question (QID),
        FOREIGN KEY (IID) REFERENCES DFintent (IID)); 
