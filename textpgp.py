#!/usr/bin/python2

import codecs
import os
import shutil
import sys
import re
import commands
import time
import gnupg
import subprocess

b = commands.getstatusoutput('ps -ef | grep e2apgp.py |wc -l')
c = int(b[1])

#Getting the log file name

timestr = time.strftime("%Y%m%d")
log_filenm = '/trans/LOGS/'+'e2apgp_'+timestr+'.log'
fle = open(log_filenm,'a+')

if c > 3:
 fle.write('\n --------------------------------------------------------------------------------------\n')
 fle.write('\n Script e2apgp.py is running already '+time.strftime("%Y%m%d-%H%M%S%s")+'\n')
 fle.write('\n --------------------------------------------------------------------------------------\n')
else:
 fle.write('\n--------------------------------------------------------------------------------------------\n')
 fle.write('\n--------- Started to convert the file for this run '+time.strftime("%Y%m%d-%H%M%S%s")+' -------\n')
 fle.write('\n--------------------------------------------------------------------------------------------\n')

 e2a_flnme = ['PREP']
 file_dict = {}
# path = '/PREP_EBSDIC_AE_FULL/' # Get current working directory
# path = '/mft/data/nonedi/hold/py/pre/'
 path = '/pgp/py/scan/'
 direc = os.listdir(path)

 for f in direc:
  name,ext = os.path.splitext(f)
  a=f.split('.')[0]
  file_dict[f] = a

 for k,v in file_dict.iteritems():
 # src = '/PREP_EBSDIC_AE_FULL/'
 # src = '/mft/data/nonedi/hold/py/pre/'
  src = '/pgp/py/scan/'
  src+=k
  fle.write('\n *****************************************************************************\n')
  fle.write('\n Start processing the file ' +k)
  shutil.copy(src, '/pgp/py/archive/')
  try:
     if v in e2a_flnme:
         isparaexist = 'NO'
         ae = re.split('\.',k)[5]
         sndnode = re.split('\.',k)[1]
         trdnode = re.split('\.',k)[3]
         aifnode = re.split('\.',k)[2]
         sevnode = re.split('\.',k)[7]
         sndnodesub = re.split('\_',k)[1]
         sndnodesub1 = re.split('\.',sndnodesub)[0]
         trdnodenozero = trdnode.lstrip('0')
         comba = sndnode + '.' + trdnodenozero
         combadot = re.sub(r'(?is)_','.',comba)
         combadir = '/custom/tables/' + combadot
         if os.path.exists(combadir):
            #isparaexist = 'YES'
            fle.write('\n Configuration file is present in '+combadir)
            with open(combadir) as dr:
             e2a_val = dr.read()
             e2a_val2 = e2a_val.split('|')
             e2a_val4 = e2a_val.split('|')[3]
             e2a_val3 = e2a_val2[3]
             e2a_val5 = e2a_val2[1]
            sa = k
            #print sa
            if ae == "E" and e2a_val3 == "A":
              #print 'am here case 1'
              isparaexist = 'YES'
              encryp_data = open(src,'r').read()
              fle.write('\n PGP decryption started')
              gpg = gnupg.GPG(gnupghome="/.gnupg/")
              decrypted_data = gpg.decrypt(encryp_data,passphrase='XXXXXXXXXXXX|XXXXXXXXXXXX')
              dcpgpok = decrypted_data.ok
              dcpgpstatus = decrypted_data.status
              fle.write('\n' +dcpgpstatus)
              dcpgpstderr = decrypted_data.stderr
              fle.write('\n' +dcpgpstderr)
              decrypted_string = str(decrypted_data)
              decrypted_data = ""
              fle.write('\n PGP decryption ended')
              #print ('PGP decryption ended')
              pos = re.split('\.',sa)[3]
              pos1 = (pos.lstrip('0'))
              pos2 = '"(.{'+pos1+'})"'
              decrylist = []
              #print pos1
              #print pos2
              str1  = []
              #print ('befire open')
              case1 = 0
              cnt = 0
              pos4 = int(pos1)
              allstrwr22 = open('/pgp/py/tmp/post/'+k+'.afconv','w')
              while case1 < len(decrypted_string):
                  split1 = decrypted_string[case1:case1+pos4]
                  case1 = case1+pos4
                  ascii_txt = codecs.decode(split1, "cp037")+'\n'
                  realascii = ascii_txt.encode('iso-8859-1')
                  allstrwr22.write(realascii)
              allstrwr22.close()
              decrypted_string = ""
              tempascii = '/pgp/py/tmp/post/'+k+'.afconv'
              sslprase = "XXXXXXXXXXXX"
              sslprotect = os.system("openssl enc -aes-256-cbc -salt -in " + tempascii + " -out " + tempascii + ".pwd -k " + sslprase)
              sslval = tempascii + ".pwd"
              os.remove(tempascii)
              sslread = subprocess.check_output("openssl enc -aes-256-cbc -d -in " + sslval + " -k " + sslprase, shell=True)
              os.remove(sslval)
              fle.write('\n Converted ' +k+ ' ebcdic file into ASCII')
              fle.write('\n PGP encryption started')
              encrypted_data = gpg.encrypt(sslread,'CleoPGP')
              encrypted_string = str(encrypted_data)
              pgpok = encrypted_data.ok
              pgpstatus = encrypted_data.status
              fle.write('\n' +pgpstatus)
              pgpstderr = encrypted_data.stderr
              fle.write('\n' +pgpstderr)
              if not e2a_val5 or e2a_val5 == '*':
               allstr1 = open('/NON_EDI/xmitscan/ASCII.'+sndnode+'.'+aifnode+'.'+sevnode,'w')
               allstr1.write(encrypted_string)
               allstr1.close()
              else:
               allstr1 = open('/NON_EDI/xmitscan/ASCII.'+e2a_val5+'_'+sndnodesub1+'.'+aifnode+'.'+sevnode,'w')
               allstr1.write(encrypted_string)
               allstr1.close()
              fle.write('\n PGP encryption ended')
              fle.write('\n The file '+k+' has encrypted and placed  under the directory /NON_EDI/xmitscan/ \n')
              if os.path.isfile(src):
                 os.remove(src)
              fle.write('\n *****************************************************************************\n')
            elif ae == "E" and e2a_val3 == "E":
             #print 'am here case 2'
             if os.path.isfile(combadir):
              isparaexist = 'YES'
              encryp_data1 = open(src,'r').read()
              fle.write('\n PGP decryption started')
              gpg = gnupg.GPG(gnupghome="/.gnupg/")
              decrypted_data1 = gpg.decrypt(encryp_data1,passphrase='XXXXXXXXXXXX|XXXXXXXXXXXX')
              dcpgpok1 = decrypted_data1.ok
              dcpgpstatus1 = decrypted_data1.status
              fle.write('\n' +dcpgpstatus1)
              dcpgpstderr1 = decrypted_data1.stderr
              fle.write('\n' +dcpgpstderr1)
              decrypted_string1 = str(decrypted_data1)
              decrypted_data1 = ""
              fle.write('\n PGP decryption ended')
              fle.write('\n PGP encryption started')
              encrypted_data2 = gpg.encrypt(decrypted_string1,'CleoPGP')
              encrypted_string2 = str(encrypted_data2)
              pgpok2 = encrypted_data2.ok
              pgpstatus2 = encrypted_data2.status
              fle.write('\n' +pgpstatus2)
              pgpstderr2 = encrypted_data2.stderr
              fle.write('\n' +pgpstderr2)
              if not e2a_val5 or e2a_val5 == '*':
               allstr2 = open('/NON_EDI/xmitscan/EBCDIC.'+sndnode+'.'+aifnode+'.'+sevnode,'w')
               allstr2.write(encrypted_string2)
               allstr2.close()
              else:
               allstr2 = open('/NON_EDI/xmitscan/EBCDIC.'+e2a_val5+'_'+sndnodesub1+'.'+aifnode+'.'+sevnode,'w')
               allstr2.write(encrypted_string2)
               allstr2.close()
              fle.write('\n PGP encryption ended')
              fle.write('\n The file '+k+' has config file and the value is "E" so sending the file as is without converting ebcdic to ASCII and placed the file under the directory /NON_EDI/xmitscan/ \n')
              if os.path.isfile(src):
                 os.remove(src)
              fle.write('\n *****************************************************************************\n')
             else:
              #print ('no files for asis')
              fle.write('\n The file '+k+' has no config file')
         elif ae == "E" and isparaexist == 'NO':
          #print 'am here'
          sa = k
          fle.write('\n There is no config file exists and converting the ebcdic file into ASCII')
          encryp_data2 = open(src,'r').read()
          fle.write('\n PGP decryption started')
          gpg = gnupg.GPG(gnupghome="/.gnupg/")
          decrypted_data2 = gpg.decrypt(encryp_data2,passphrase='XXXXXXXXXXXX|XXXXXXXXXXXX')
          dcpgpok2 = decrypted_data2.ok
          dcpgpstatus2 = decrypted_data2.status
          fle.write('\n' +dcpgpstatus2)
          dcpgpstderr2 = decrypted_data2.stderr
          fle.write('\n' +dcpgpstderr2)
          decrypted_string1 = str(decrypted_data2)
          fle.write('\n PGP decryption ended')
          posr = re.split('\.',sa)[3]
          posr1 = (posr.lstrip('0'))
          posr2 = '"(.{'+posr1+'})"'
          case3 = 0
          cnt3 = 0
          posr4 = int(posr1)
          allstrwr33 = open('/pgp/py/tmp/post/'+k+'.afconv','w')
          while case3 < len(decrypted_string1):
              split3 = decrypted_string1[case3:case3+posr4]
              case3 = case3+posr4
              ascii_txt3 = codecs.decode(split3, "cp037")+'\n'
              realascii3 = ascii_txt3.encode('iso-8859-1')
              allstrwr33.write(realascii3)
          allstrwr33.close()
          decrypted_string1 = ""
          tempascii3 = '/pgp/py/tmp/post/'+k+'.afconv'
          sslprase3 = "XXXXXXXXXXXX"
          sslprotect3 = os.system("openssl enc -aes-256-cbc -salt -in " + tempascii3 + " -out " + tempascii3 + ".pwd -k " + sslprase3)
          sslval3 = tempascii3 + ".pwd"
          os.remove(tempascii3)
          sslread3 = subprocess.check_output("openssl enc -aes-256-cbc -d -in " + sslval3 + " -k " + sslprase3, shell=True)
          os.remove(sslval3)
          fle.write('\n Converted ' +k+ ' ebcdic file into ASCII')
          fle.write('\n PGP encryption started')
          encrypted_data = gpg.encrypt(sslread3,'CleoPGP')
          encrypted_string = str(encrypted_data)
          pgpok = encrypted_data.ok
          pgpstatus = encrypted_data.status
          fle.write('\n' +pgpstatus)
          pgpstderr = encrypted_data.stderr
          fle.write('\n' +pgpstderr)
          allstrr1 = open('/NON_EDI/xmitscan/ASCII.'+sndnode+'.'+aifnode+'.'+sevnode,'w')
          allstrr1.write(encrypted_string)
          allstrr1.close()
          fle.write('\n PGP encryption ended')
          fle.write('\n The file '+k+' has encrypted and placed  under the directory /NON_EDI/xmitscan/ \n')
          if os.path.isfile(src):
           os.remove(src)
          fle.write('\n *****************************************************************************\n')
         elif ae == "A" and isparaexist == 'NO':
          sa = k
          fle.write('\n There is no config file exists and sending file as is')
          encryp_data3 = open(src,'r').read()
          fle.write('\n PGP decryption started')
          gpg = gnupg.GPG(gnupghome="/.gnupg/")
          decrypted_data3 = gpg.decrypt(encryp_data3,passphrase='XXXXXXXXXXXX|XXXXXXXXXXXX')
          dcpgpok3 = decrypted_data3.ok
          dcpgpstatus3 = decrypted_data3.status
          fle.write('\n' +dcpgpstatus3)
          dcpgpstderr3 = decrypted_data3.stderr
          fle.write('\n' +dcpgpstderr3)
          decrypted_string3 = str(decrypted_data3)
          fle.write('\n PGP decryption ended')
          fle.write('\n PGP encryption started')
          encrypted_data = gpg.encrypt(decrypted_string3,'CleoPGP')
          encrypted_string4 = str(encrypted_data)
          pgpok = encrypted_data.ok
          pgpstatus = encrypted_data.status
          fle.write('\n' +pgpstatus)
          pgpstderr = encrypted_data.stderr
          fle.write('\n' +pgpstderr)
          allstrr4 = open('/NON_EDI/xmitscan/EBCDIC.'+sndnode+'.'+aifnode+'.'+sevnode,'w')
          allstrr4.write(encrypted_string4)
          allstrr4.close()
          fle.write('\n PGP encryption ended')
          fle.write('\n The file '+k+' has encrypted and placed  under the directory /NON_EDI/xmitscan/ \n')
          if os.path.isfile(src):
           os.remove(src)
          fle.write('\n *****************************************************************************\n')
     else:
        #print('\n File missing or picked by other application ')
        fle.write('\n File missing or picked by other application')
  except Exception as errr:
       #print(errr)
       fle.write('\n Something went wrong with the file or Something wrong with the program1'+errr)
  except IOError, e:
       #print(e)
       fle.write('\n Something went wrong with the file or Something wrong with the program'+ e)
 fle.write('\n--------------------------------------------------------------------------------------------\n')
 fle.write('\n--------- The run is completed '+time.strftime("%Y%m%d-%H%M%S%s")+' -------\n')
 fle.write('\n--------------------------------------------------------------------------------------------\n')

