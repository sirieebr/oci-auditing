# User configurations on OCI

These mandatory details will be required for the configuration:
* RSA key pair in PEM format
* Tenancy name
* Tenancy OCID
* User OCID
* API fingerprint of the user

<br />
<br />

Login to your OCI console and click on the Profile button > Tenancy.

![](./images/image003.jpg)

On the Tenancy Details page, find the OCID and click on "Show" to view the complete OCID or click on "Copy" to copy it into clipboard and paste on a notepad.

![](./images/image004.jpg)

In the OCI console, click on the Profile button > Username.

![](./images/image005.jpg)

On the User Details page, find the user OCID and click on "Show" to view the complete OCID or click on "Copy" to copy it into clipboard and paste on a notepad.

![](./images/image006.jpg)

\* Upload the public key "oci_api_key_public.pem" generated. {[How to generate RSA key pair](./rsa_key_pair_generation.md)}

\* On the User Details page, scroll down to Resources and click on API Keys > Add Public Key.

\* Select or drop the public key and hit "Add".

![](./images/image007.jpg)

\* A fingerprint will be generated. Copy this fingerprint and keep handy on a notepad.

![](./images/image008.jpg)

<br />

_Note: In similar way, get details of all other tenancies in scope for audit._

