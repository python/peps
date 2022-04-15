resource "fastly_service_vcl" "peps" {
  name     = "peps.python.org"
  activate = true
  domain { name = "peps.python.org" }

  backend {
    name          = "GitHub Pages"
    address       = "python.github.io"
    port          = 443
    override_host = "peps.python.org"

    use_ssl           = true
    ssl_check_cert    = true
    ssl_cert_hostname = "python.github.io"
    ssl_sni_hostname  = "python.github.io"
  }

  header {
    name          = "HSTS"
    type          = "response"
    action        = "set"
    destination   = "http.Strict-Transport-Security"
    ignore_if_set = false
    source        = "\"max-age=31536000; includeSubDomains; preload\""
  }

  request_setting {
    name      = "Force TLS"
    force_ssl = true
  }

  snippet {
    name    = "serve-rss"
    type    = "recv"
    content = <<-EOT
        if (req.url == "/peps.rss/") {
          set req.url = "/peps.rss";
        }
    EOT
  }

  snippet {
    name    = "redirect"
    type    = "error"
    content = <<-EOT
        if (obj.status == 618) {
          set obj.status = 302;
          set obj.http.Location = "https://" + req.http.host + req.http.Location;
          return(deliver);
        }
    EOT
  }
  snippet {
    name    = "redirect-numbers"
    type    = "recv"
    content = <<-EOT
        if (req.url ~ "^/(\d|\d\d|\d\d\d|\d\d\d\d)/?$") {
          set req.http.Location = "/pep-" + std.strpad(re.group.1, 4, "0") + "/";
          error 618;
        }
    EOT
  }
  snippet {
    name    = "left-pad-pep-numbers"
    type    = "recv"
    content = <<-EOT
        if (req.url ~ "^/pep-(\d|\d\d|\d\d\d)/?$") {
          set req.http.Location = "/pep-" + std.strpad(re.group.1, 4, "0") + "/";
          error 618;
        }
    EOT
  }
}
