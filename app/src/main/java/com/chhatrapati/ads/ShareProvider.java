package com.chhatrapati.ads;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileNotFoundException;

/** Read-only provider that hands cached full-HD files to WhatsApp and other share targets. */
public class ShareProvider extends ContentProvider {
    static File file(Context ctx, Item item) {
        File dir = new File(ctx.getCacheDir(), "share");
        dir.mkdirs();
        return new File(dir, item.date + "_" + item.file);
    }

    static Uri uri(Context ctx, File f) {
        return Uri.parse("content://" + ctx.getPackageName() + ".share/" + Uri.encode(f.getName()));
    }

    private File resolve(Uri uri) throws FileNotFoundException {
        String name = uri.getLastPathSegment();
        if (name == null || name.contains("/") || name.contains("..")) throw new FileNotFoundException();
        File f = new File(new File(getContext().getCacheDir(), "share"), name);
        if (!f.exists()) throw new FileNotFoundException(name);
        return f;
    }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        return ParcelFileDescriptor.open(resolve(uri), ParcelFileDescriptor.MODE_READ_ONLY);
    }

    @Override
    public String getType(Uri uri) {
        String p = uri.getPath() == null ? "" : uri.getPath().toLowerCase();
        if (p.endsWith(".mp4")) return "video/mp4";
        if (p.endsWith(".png")) return "image/png";
        return "image/jpeg";
    }

    @Override
    public Cursor query(Uri uri, String[] projection, String sel, String[] args, String sort) {
        try {
            File f = resolve(uri);
            MatrixCursor c = new MatrixCursor(new String[]{OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE});
            c.addRow(new Object[]{f.getName(), f.length()});
            return c;
        } catch (FileNotFoundException e) {
            return null;
        }
    }

    @Override
    public boolean onCreate() {
        return true;
    }

    @Override
    public Uri insert(Uri uri, ContentValues values) {
        return null;
    }

    @Override
    public int delete(Uri uri, String sel, String[] args) {
        return 0;
    }

    @Override
    public int update(Uri uri, ContentValues values, String sel, String[] args) {
        return 0;
    }
}
