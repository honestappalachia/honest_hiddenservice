# Mon Feb 18 17:08:39 PST 2013

`UPLOAD_DIR` should be in /tmp, which should be an encrypted
tmpfs/ramfs. Then we don't need to use shred, and can be more comfortable on
a wider array of filesystems/disk types (jury's still out on secure deleting
SSD's). Will need it's own set of unique checks though. For more:
http://www.thegeekstuff.com/2008/11/overview-of-ramfs-and-tmpfs-on-linux/.

# Mon Feb 18 17:08:53 PST 2013

Should pull request beanstalkc and add support for using `with`. Looks like
I just need to add an `__exit__` function?

# Wed Mar  6 19:46:41 PST 2013

We want to create a unique ID that will identify an upload with revealing
anything about it. This can be done by hashing the filename, file contents,
upload timestamp, and a random salt. Using the file contents may prove to be
excessively slow, and may not be necessary. This hash will be used in saving
the file and will be returned to the uploader as a unique ID that they can
later use to discuss their upload.

TODO: come back and reconsider this, especially possible hash-guessing attacks
launched against the discussion site.

There are a lot of possibilites for dealing with the resulting file in a way
that reduces the utility of forensics. We used to just shred the files, but
this is both filesystem and backing storage (only works on magnetic HDDs)
dependent. Given the increasing prevalence of SSDs in servers, this is no
longer a viable assumption. A better solution would be to create an encrypted
file system as a one-time workspace (glovebox, darkroom) for receiving the
upload and preparing it.

All of this is quite tricky to do completely properly, unfortunately. Since
I am using Python for the web application, it is very difficult (and maybe
impossible) to be sure about data remnance for the data stream of the upload,
as well as any passphrases generated for the encrypted workspace. The memset
solution with ctypes is worth investigating.

Ultimately, the best solution might be to write the upload site as a CGI script
in C in order to esure secure deletion of this type of sensitive information.
That would be quite an undertaking, but may be the only way.

Actually, I think we can get away with the initial (fairly simple) plan. Create
a system with no swap (watch out for patterns that might use too much memory
and cause a crash, and related DoS possibilities), and make /tmp a ramfs that
is encrypted by a C program (which safely disposes of the ephemeral encryption
key immediately), and then use that as the volatile scratch space. This creates
a "burn after reading" space where

1. data remnance can be avoided by simply deleting and zero-filling the files,
   since they are on a ramfs
2. encryption necessary?

We then still have the problems of RAM remnance overall (possibly resolved by
smem from secure-delete) and RAM remnance in a long-running Python process
(unresolved). It may be worth investigating using the ctypes/cffi memset
approach here.

Good stuff from the openBSD project on encrypted swap: http://static.usenix.org/events/sec2000/full_papers/provos/provos_html/index.html
