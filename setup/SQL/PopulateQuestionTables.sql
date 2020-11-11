-- populate question table
USE HeadacheBot;

INSERT INTO question (QID, qText)
		VALUES (1, 'Do you have a headache?');
        
INSERT INTO question (QID, qText)
		VALUES (2, 'Are you reporting a headache you had?');

INSERT INTO question (QID, qText)
		VALUES (3, 'Are you reporting a medication you took?');
        
 INSERT INTO question (QID, qText)
		VALUES (4, 'Have a wonderful day!');

INSERT INTO question (QID, qText)
		VALUES (5, 'What name do you give this headache?');
        
INSERT INTO question (QID, qText)
		VALUES (6, 'Did you wake up with this headache?');
        
INSERT INTO question (QID, qText)
		VALUES (7, 'What is/was the duration of your headache?');
        
INSERT INTO question (QID, qText)
		VALUES (8, 'How severe is your headache?');
        
INSERT INTO question (QID, qText)
		VALUES (9, 'How many times has it happened since you wokeup?');
        
INSERT INTO question (QID, qText)
		VALUES (10, 'For this headache, did you take medication?');
        
INSERT INTO question (QID, qText)
		VALUES (11, 'What medication was it?');
        
INSERT INTO question (QID, qText)
		VALUES (12, 'How many pills?');

INSERT INTO question (QID, qText)
		VALUES (13, 'Did this medication help your headache?');

INSERT INTO question (QID, qText)
		VALUES (14, 'How severe was your headache prior to medication?');

INSERT INTO question (QID, qText)
		VALUES (15, 'Did you experience another form of headache?');
        
INSERT INTO question (QID, qText)
		VALUES (16, 'If female, are you in the middle or close to your menstruation cycle?');
        
INSERT INTO question (QID, qText)
		VALUES (17, 'Did you go to a physician for this headache?');
        
INSERT INTO question (QID, qText)
		VALUES (18, 'Was it a USC facility?');

INSERT INTO question (QID, qText)
		VALUES (19, 'Thank you for recording your headache. You may always review and edit your current or previous response.');
        
-- populate leads_to
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (1, 2, 'No');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (1, 5, 'Yes');

INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (2, 5, 'Yes');

INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (2, 3, 'No');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (3, 4, 'No');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (3, 11, 'Yes');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (5, 6, 'Record: name');

-- no '/' character for ease of creating parameter names later on
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (6, 7, 'Record: YesNo');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (7, 8, 'Record: duration');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (8, 9, 'Record: severity');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (9, 10, 'Record: count');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (10, 11, 'Yes');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (10, 15, 'No');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (11, 12, 'Record: response');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (12, 13, 'Record: response');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (13, 14, 'Yes');
	
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (13, 15, 'No');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (14, 15, 'Record: response');

INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (15, 16, 'No');

INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (15, 5, 'Yes');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (16, 17, 'Record: response');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (17, 19, 'No');

INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (17, 18, 'Yes');
        
INSERT INTO leads_to (parentQID, childQID, response)
		VALUES (18, 19, 'Record: response');
	
