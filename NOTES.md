# Mon Feb 18 17:08:39 PST 2013

`UPLOAD_DIR` should be in /tmp, which should be an encrypted
tmpfs/ramfs. Then we don't need to use shred, and can be more comfortable on
a wider array of filesystems/disk types (jury's still out on secure deleting
SSD's). Will need it's own set of unique checks though. For more:
http://www.thegeekstuff.com/2008/11/overview-of-ramfs-and-tmpfs-on-linux/.

# Mon Feb 18 17:08:53 PST 2013

Should pull request beanstalkc and add support for using `with`. Looks like
I just need to add an `__exit__` function?
