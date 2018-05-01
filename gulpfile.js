// Sass configuration
var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');

gulp.task('sass', function() {
    gulp.src('./scss/**/*.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('./benwaonline/static/css/'));
});

gulp.task('default', ['sass'], function() {
    gulp.watch('./scss/**/*.scss', ['sass']);
})