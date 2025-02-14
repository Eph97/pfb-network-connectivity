# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 1.8"


PFB_SHARED_FOLDER_TYPE = ENV.fetch("PFB_SHARED_FOLDER_TYPE", "nfs")

if PFB_SHARED_FOLDER_TYPE == "nfs"
  if Vagrant::Util::Platform.linux? then
    PFB_MOUNT_OPTIONS = ['rw', 'tcp', 'nolock', 'actimeo=1']
  else
    PFB_MOUNT_OPTIONS = ['vers=3', 'udp', 'actimeo=1']
  end
else
  if ENV.has_key?("PFB_MOUNT_OPTIONS")
    PFB_MOUNT_OPTIONS = ENV.fetch("PFB_MOUNT_OPTIONS").split
  else
    PFB_MOUNT_OPTIONS = ["rw"]
  end
end
VAGRANT_NETWORK_OPTIONS = { auto_correct: false }

ROOT_VM_DIR = "/vagrant"

Vagrant.configure("2") do |config|

  config.vm.box = "bento/ubuntu-20.04"
  config.vm.hostname = "pfb-network-connectivity"
  config.vm.network :private_network, ip: ENV.fetch("PFB_PRIVATE_IP", "192.168.56.12")

  config.vm.network :forwarded_port, guest: 9200, host: ENV.fetch("PFB_NGINX_PORT", 9200)
  config.vm.network :forwarded_port, guest: 9202, host: ENV.fetch("PFB_GUNICORN_PORT", 9202)
  config.vm.network :forwarded_port, guest: 9203, host: ENV.fetch("PFB_RUNSERVER_PORT", 9203)
  config.vm.network :forwarded_port, guest: 5432, host: ENV.fetch("PFB_ANALYSIS_DB_PORT", 9214)
  config.vm.network :forwarded_port, guest: 9301, host: ENV.fetch("PFB_REPOSITORY_PORT", 9301)
  config.vm.network :forwarded_port, guest: 9302, host: ENV.fetch("PFB_REPOSITORY_PORT", 9302)
  config.vm.network :forwarded_port, guest: 9400, host: ENV.fetch("PFB_TILEGARDEN_PORT", 9400)
  config.vm.network :forwarded_port, guest: 9401, host: ENV.fetch("PFB_TILEGARDEN_DEBUG_PORT", 9401)

  config.vm.synced_folder "~/.aws", "/home/vagrant/.aws"
  config.vm.synced_folder '.', ROOT_VM_DIR, type: PFB_SHARED_FOLDER_TYPE, mount_options: PFB_MOUNT_OPTIONS

  config.vm.provision "shell" do |s|
    s.path = 'deployment/vagrant/cd_shared_folder.sh'
    s.args = "'#{ROOT_VM_DIR}'"
  end

  config.vm.provision "shell" do |s|
    # The base box comes with a 64GB virtual disk but only 30GB is actually included
    # in the filesystem. This extends the logical volume within the VM and expands the
    # filesystem to use all of it.
    # Ignores errors, since it will return an error if it has already been done.
    s.inline = <<-SHELL
      sudo lvextend -l +100%FREE --resizefs /dev/ubuntu-vg/ubuntu-lv \
          || echo "Extending logical volume failed. Continuing anyway."
    SHELL
  end

  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "deployment/ansible/pfb.yml"
    ansible.galaxy_role_file = "deployment/ansible/roles.yml"
    ansible.verbose = true
    ansible.raw_arguments = ["--timeout=60",
                             "--extra-vars",
                             "dev_user=#{ENV.fetch("USER", "vagrant")}"]

    # local arguments
    ansible.install = true
    ansible.install_mode = "pip"
    # Install pip3 for the system version of python3, and make sure 'pip3' works as well
    ansible.pip_install_cmd = "sudo apt-get install -y python3-pip && sudo ln -s -f /usr/bin/pip3 /usr/bin/pip"
    ansible.version = "2.8.7"
  end

  config.vm.provider :virtualbox do |v|
    v.memory = ENV.fetch("PFB_MEM", 4096)
    v.cpus = ENV.fetch("PFB_CPUS", 8)
  end
end
