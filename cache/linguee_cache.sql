create table if not exists linguee_cache (
    id bytea primary key,
    url text not null,
    status_code int not null,
    content bytea not null
);
