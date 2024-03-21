-- SQL script that creates a stored procedure ComputeAverageWeightedScoreForUsers that computes and store the average weighted score for all students
DELIMITER $$

CREATE PROCEDURE ComputeAverageWeightedScoreForUsers()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE user_id INT;
    DECLARE total_score FLOAT;
    DECLARE total_weight INT;
    DECLARE weighted_avg FLOAT;

    -- Cursor to iterate through each user
    DECLARE cur CURSOR FOR SELECT id FROM users;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO user_id;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Calculate total weighted score and total weight for the user
        SELECT SUM(corrections.score * projects.weight), SUM(projects.weight)
        INTO total_score, total_weight
        FROM corrections
        JOIN projects ON corrections.project_id = projects.id
        WHERE corrections.user_id = user_id;

        -- Calculate weighted average score
        IF total_weight > 0 THEN
            SET weighted_avg = total_score / total_weight;
        ELSE
            SET weighted_avg = 0;
        END IF;

        -- Update user's average_score
        UPDATE users SET average_score = weighted_avg WHERE id = user_id;
    END LOOP;

    CLOSE cur;
END$$

DELIMITER ;
