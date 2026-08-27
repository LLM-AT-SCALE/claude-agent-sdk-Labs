-- db/seed.sql
-- Creates exactly the 6 customers and 8 products named in
-- the reference set, and no others. No seed rows for sales: those arrive
-- through the application or the CSV loader.

INSERT INTO customer (full_name, email, city, country_code) VALUES
    ('Ava Mendez',  'ava.mendez@example.com',  'Austin',     'US'),
    ('Liu Wei',     'liu.wei@example.com',     'Singapore',  'SG'),
    ('Priya Raman', 'priya.raman@example.com', 'Bengaluru',  'IN'),
    ('Tomas Novak', 'tomas.novak@example.com', 'Brno',       'CZ'),
    ('Sara Haddad', 'sara.haddad@example.com', 'Casablanca', 'MA'),
    ('Jonas Berg',  'jonas.berg@example.com',  'Uppsala',    'SE');

INSERT INTO product (sku, name, category, unit_price) VALUES
    ('KB-ERGO-01',  'Ergonomic Split Keyboard',      'Peripherals', 189.00),
    ('MS-TRACK-02', 'Trackball Mouse',                'Peripherals', 79.50),
    ('MN-27U-4K',   '27-inch 4K Monitor',             'Displays',    429.99),
    ('MN-34UW-QHD', '34-inch Ultrawide QHD Monitor',  'Displays',    699.00),
    ('DK-USBC-90W', 'USB-C Docking Station 90W',      'Accessories', 245.00),
    ('HS-ANC-PRO',  'Noise-Cancelling Headset',       'Audio',       312.75),
    ('WC-1080-STR', '1080p Streaming Webcam',         'Video',       96.25),
    ('ST-NVME-2TB', '2TB NVMe SSD',                   'Storage',     158.40);
