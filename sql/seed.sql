-- Add missing demo rows only; preserve existing names, coordinates and road speeds.
-- The Python initializer checks schema compatibility before executing this file.
START TRANSACTION;
INSERT INTO locations (name,x,y) SELECT 'Majestic',0,0 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE name='Majestic');
INSERT INTO locations (name,x,y) SELECT 'Vidhana Soudha',2,0 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE name='Vidhana Soudha');
INSERT INTO locations (name,x,y) SELECT 'Cubbon Park',0,3 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE name='Cubbon Park');
INSERT INTO locations (name,x,y) SELECT 'MG Road',4,0 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE name='MG Road');
INSERT INTO locations (name,x,y) SELECT 'Indiranagar',6,0 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE name='Indiranagar');
INSERT INTO locations (name,x,y) SELECT 'Whitefield',8,3 WHERE NOT EXISTS (SELECT 1 FROM locations WHERE name='Whitefield');
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,30 FROM locations a JOIN locations b ON b.name='Vidhana Soudha' WHERE a.name='Majestic' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,30 FROM locations a JOIN locations b ON b.name='Majestic' WHERE a.name='Vidhana Soudha' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,30 FROM locations a JOIN locations b ON b.name='MG Road' WHERE a.name='Vidhana Soudha' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,30 FROM locations a JOIN locations b ON b.name='Vidhana Soudha' WHERE a.name='MG Road' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,60 FROM locations a JOIN locations b ON b.name='Cubbon Park' WHERE a.name='Majestic' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,60 FROM locations a JOIN locations b ON b.name='Majestic' WHERE a.name='Cubbon Park' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,60 FROM locations a JOIN locations b ON b.name='MG Road' WHERE a.name='Cubbon Park' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,60 FROM locations a JOIN locations b ON b.name='Cubbon Park' WHERE a.name='MG Road' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,40 FROM locations a JOIN locations b ON b.name='Indiranagar' WHERE a.name='MG Road' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
INSERT INTO roads (source_id,target_id,speed_kmph) SELECT a.id,b.id,40 FROM locations a JOIN locations b ON b.name='MG Road' WHERE a.name='Indiranagar' AND NOT EXISTS (SELECT 1 FROM roads r WHERE r.source_id=a.id AND r.target_id=b.id);
COMMIT;
