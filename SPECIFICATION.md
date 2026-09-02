# System Specification: Music Album Catalog

## 1. Overview and Purpose

This document specifies the architecture, data models, and API contracts for the Music Album Catalog system.
The system implements Specification-Driven Development (SDD).
The specification defines requirements, database structures, constraints, and REST API behavior before code generation.

---

## 2. Domain Model and Business Rules

### 2.1 Entities

#### Artist
- Represents a musical artist or group.
- Attributes:
  - `id`: Integer primary key.
  - `name`: String, required, unique, maximum length 255 characters.
  - `created_at`: Timestamp.
  - `updated_at`: Timestamp.

#### Album
- Represents a released music collection.
- Attributes:
  - `id`: Integer primary key.
  - `title`: String, required, maximum length 255 characters.
  - `artist_id`: Foreign key reference to Artist, required.
  - `release_year`: Integer, required, valid range 1900 to 2100.
  - `created_at`: Timestamp.
  - `updated_at`: Timestamp.

#### Song
- Represents a musical composition.
- Attributes:
  - `id`: Integer primary key.
  - `title`: String, required, maximum length 255 characters.
  - `created_at`: Timestamp.
  - `updated_at`: Timestamp.

#### Track (AlbumSong)
- Represents the association between an Album and a Song.
- Attributes:
  - `id`: Integer primary key.
  - `album_id`: Foreign key reference to Album, required.
  - `song_id`: Foreign key reference to Song, required.
  - `track_number`: Integer, required, positive value (>= 1).

### 2.2 Core Business Rules

1. **Many-to-Many Song Association**:
   A single Song can belong to multiple Albums.
   In each Album, the Song can hold a different `track_number`.
2. **Track Number Uniqueness within Album**:
   No two tracks within the same Album can share the same `track_number`.
   Constraint: `UNIQUE (album_id, track_number)`.
3. **Song Uniqueness within Album**:
   The same Song cannot be added more than once to the same Album.
   Constraint: `UNIQUE (album_id, song_id)`.
4. **Referential Integrity**:
   - Deleting an Artist deletes all dependent Albums (CASCADE).
   - Deleting an Album deletes all associated Track mappings (CASCADE), but preserves Song entities.
   - Deleting a Song removes its Track mappings from all Albums (CASCADE), but preserves Album entities.

---

## 3. Database Relational Schema

```sql
CREATE TABLE catalog_artist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE catalog_album (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    artist_id INTEGER NOT NULL REFERENCES catalog_artist(id) ON DELETE CASCADE,
    release_year INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE catalog_song (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE catalog_albumsong (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL REFERENCES catalog_album(id) ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES catalog_song(id) ON DELETE CASCADE,
    track_number INTEGER NOT NULL CHECK (track_number > 0),
    CONSTRAINT unique_album_track_number UNIQUE (album_id, track_number),
    CONSTRAINT unique_album_song UNIQUE (album_id, song_id)
);

CREATE INDEX idx_album_artist ON catalog_album(artist_id);
CREATE INDEX idx_album_year ON catalog_album(release_year);
CREATE INDEX idx_track_album ON catalog_albumsong(album_id);
CREATE INDEX idx_track_song ON catalog_albumsong(song_id);
```

---

## 4. REST API Specification

Base URL: `/api/v1`

### 4.1 Artists Endpoints

- `GET /api/v1/artists/`
  - Query parameters:
    - `search`: Filter by artist name substring.
  - Response 200: Array of Artist objects with `albums_count`.
- `POST /api/v1/artists/`
  - Request body: `{"name": "Artist Name"}`
  - Response 201: Created Artist object.
  - Response 400: Validation error.
- `GET /api/v1/artists/{id}/`
  - Response 200: Artist object with list of released albums.
  - Response 404: Not found.
- `PUT /api/v1/artists/{id}/` & `PATCH /api/v1/artists/{id}/`
  - Update artist name.
- `DELETE /api/v1/artists/{id}/`
  - Response 204: Deletion confirmed.

### 4.2 Albums Endpoints

- `GET /api/v1/albums/`
  - Query parameters:
    - `search`: Filter by album title or artist name.
    - `artist`: Filter by artist ID.
    - `year`: Filter by release year.
    - `year_min`, `year_max`: Range filter.
  - Response 200: Array of Album objects including nested artist data and tracks count.
- `POST /api/v1/albums/`
  - Request body:
    ```json
    {
      "title": "A Night at the Opera",
      "artist_id": 1,
      "release_year": 1975,
      "tracks": [
        {"song_title": "Death on Two Legs", "track_number": 1},
        {"song_id": 4, "track_number": 11}
      ]
    }
    ```
  - Response 201: Created Album with full tracklist.
- `GET /api/v1/albums/{id}/`
  - Response 200: Detailed Album object with ordered tracklist.
- `PUT /api/v1/albums/{id}/` & `PATCH /api/v1/albums/{id}/`
  - Update album title, artist, year, or tracklist.
- `DELETE /api/v1/albums/{id}/`
  - Response 204: Deletion confirmed.
- `POST /api/v1/albums/{id}/tracks/`
  - Add or update a track in the album.
  - Request body: `{"song_id": 2, "track_number": 5}` or `{"song_title": "New Track", "track_number": 5}`
- `DELETE /api/v1/albums/{id}/tracks/{track_id}/`
  - Remove track from album.

### 4.3 Songs Endpoints

- `GET /api/v1/songs/`
  - Query parameters:
    - `search`: Filter by song title substring.
  - Response 200: Array of Song objects with list of album appearances:
    ```json
    [
      {
        "id": 10,
        "title": "Bohemian Rhapsody",
        "albums": [
          {
            "album_id": 1,
            "album_title": "A Night at the Opera",
            "artist_name": "Queen",
            "release_year": 1975,
            "track_number": 11
          },
          {
            "album_id": 2,
            "album_title": "Greatest Hits",
            "artist_name": "Queen",
            "release_year": 1981,
            "track_number": 1
          }
        ]
      }
    ]
    ```
- `POST /api/v1/songs/`
  - Request body: `{"title": "Song Title"}`
  - Response 201: Created Song.
- `GET /api/v1/songs/{id}/`
  - Detailed song with all album references.
- `PUT /api/v1/songs/{id}/` & `PATCH /api/v1/songs/{id}/`
  - Rename song.
- `DELETE /api/v1/songs/{id}/`
  - Response 204: Deletion confirmed.

---

## 5. User Interface Specification

1. **Albums Catalog View**:
   - Filter bar: search by title/artist, filter by year.
   - Grid layout: responsive cards showing album cover, title, artist, year, and track count.
   - Quick action: Add Album dialog with dynamic tracklist builder.
2. **Album Detail View**:
   - Album header: title, artist link, release year, total tracks.
   - Tracklist table: ordered by `track_number`, showing song title and actions.
   - Inline track management: add track, remove track, reorder tracks.
3. **Artists Directory View**:
   - Artist list with album count and discography expansion.
   - Add/Edit/Delete artist dialog.
4. **Songs Library View**:
   - Master list of songs.
   - Cross-album presence badges: displays every album where the song appears with its track number.
   - Add/Edit/Delete song dialog.
5. **State Feedback**:
   - Loading skeletons during network fetches.
   - Clear empty states with call-to-action triggers.
   - Inline form error messages with field highlighting.

---

## 6. Verification and Test Specification

1. **Unit Tests (Backend)**:
   - Verify unique constraint on `(album, track_number)`.
   - Verify unique constraint on `(album, song)`.
   - Verify many-to-many relationship allowing the same song in two albums with different track numbers.
   - Verify cascade delete rules.
2. **Integration Tests (API)**:
   - Full CRUD cycle for Artists, Albums, and Songs.
   - Validation failures return HTTP 400 with field details.
   - Search and filter queries return expected subsets.
3. **Frontend Build**:
   - Production bundle compiles without warnings or errors (`npm run build`).
