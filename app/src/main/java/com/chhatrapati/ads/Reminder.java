package com.chhatrapati.ads;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import java.util.Calendar;
import java.util.TimeZone;

/** Daily 9:00 AM (India time) "today's ads are ready" notification; re-armed after each alarm and reboot. */
public class Reminder extends BroadcastReceiver {
    private static final String CHANNEL = "daily";

    static void schedule(Context ctx) {
        Calendar c = Calendar.getInstance(TimeZone.getTimeZone("Asia/Kolkata"));
        c.set(Calendar.HOUR_OF_DAY, 9);
        c.set(Calendar.MINUTE, 0);
        c.set(Calendar.SECOND, 0);
        if (c.getTimeInMillis() <= System.currentTimeMillis()) c.add(Calendar.DAY_OF_MONTH, 1);
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        // A 10-minute window lets Android batch the alarm without needing exact-alarm permission.
        am.setWindow(AlarmManager.RTC_WAKEUP, c.getTimeInMillis() - 10 * 60 * 1000L, 10 * 60 * 1000L, pending(ctx));
    }

    private static PendingIntent pending(Context ctx) {
        return PendingIntent.getBroadcast(ctx, 1, new Intent(ctx, Reminder.class).setAction("com.chhatrapati.ads.DAILY"),
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    @Override
    public void onReceive(Context ctx, Intent intent) {
        schedule(ctx);
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) return;
        L.load(ctx);
        NotificationManager nm = (NotificationManager) ctx.getSystemService(Context.NOTIFICATION_SERVICE);
        nm.createNotificationChannel(new NotificationChannel(CHANNEL,
                L.t("Daily ads", "रोज़ के ऐड"), NotificationManager.IMPORTANCE_DEFAULT));
        PendingIntent open = PendingIntent.getActivity(ctx, 0, new Intent(ctx, MainActivity.class),
                PendingIntent.FLAG_IMMUTABLE);
        Notification n = new Notification.Builder(ctx, CHANNEL)
                .setSmallIcon(android.R.drawable.ic_menu_gallery)
                .setContentTitle(L.t("Today's ads are ready", "आज के ऐड तैयार हैं"))
                .setContentText(L.t("Tap to download and share", "डाउनलोड और शेयर करने के लिए टैप करें"))
                .setContentIntent(open)
                .setAutoCancel(true)
                .build();
        try {
            nm.notify(1, n);
        } catch (SecurityException ignored) {
            // Notifications not allowed by the user.
        }
    }
}
