update res_partner set create_date = create_date_import, create_uid = create_uid_import
where create_date_import is not null;